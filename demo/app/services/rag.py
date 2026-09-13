"""义乌小商品出海智能体 - RAG 知识库检索服务

轻量级 RAG 实现（无新增依赖）：
- 语料：app/data/knowledge_base.json 领域文档 + FAQ_DATABASE 全量 FAQ
- 检索：优先走 DashScope text-embedding 向量检索（OpenAI 兼容 /embeddings 接口，
  结果缓存到 data/kb_embeddings.json，语料不变时不重复调用）；
  embedding 不可用（无 key / 网关不支持 / 超时）时自动降级为字符 bigram
  Dice 相似度检索，保证离线环境也有真实知识库命中。
- 延迟建索引：首次 retrieve 时才加载语料并向量化，不影响服务启动速度。
"""

import asyncio
import hashlib
import json
import logging
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

from ..data.customer_service_data import FAQ_DATABASE

logger = logging.getLogger(__name__)


def _data_dir() -> Path:
    """与 llm.py 的日计数路径保持同一数据目录约定"""
    db_path = os.getenv("DATABASE_PATH", "")
    base = Path(db_path).parent if db_path else Path(__file__).resolve().parent.parent.parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _bigrams(text: str) -> set:
    """字符级 bigram 集合（短文本退化为单字集合）"""
    text = text.lower()
    grams = {text[i:i + 2] for i in range(len(text) - 1)}
    return grams or set(text)


def _coverage(query_grams: set, doc_grams: set, title_grams: set) -> float:
    """查询覆盖度评分：查询 bigram 被文档覆盖的比例（标题命中加权）。

    检索场景是"短查询 vs 长文档"，Dice/Jaccard 会因文档长度天然压分导致
    长文档永远过不了阈值，故改用覆盖度：分母只看查询本身。
    """
    if not query_grams:
        return 0.0
    body = len(query_grams & doc_grams) / len(query_grams)
    title = len(query_grams & title_grams) / len(query_grams)
    return body + 0.5 * title


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class RAGService:
    """知识库检索服务：向量检索优先，bigram 降级兜底"""

    def __init__(self):
        self._docs: Optional[List[Dict[str, Any]]] = None
        self._embed_vectors: Optional[List[List[float]]] = None
        self._bigram_index: Optional[List[Tuple[set, set]]] = None  # (标题, 全文)
        self._index_lock = asyncio.Lock()
        self._index_ready = False
        self.embed_model = os.getenv("LLM_EMBED_MODEL", "text-embedding-v3")
        self.embed_min_score = float(os.getenv("RAG_EMBED_MIN_SCORE", "0.35"))
        self.bigram_min_score = float(os.getenv("RAG_BIGRAM_MIN_SCORE", "0.2"))
        self._cache_file = _data_dir() / "kb_embeddings.json"

    # ---------- 语料加载 ----------

    def _load_docs(self) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        kb_file = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"
        try:
            raw = json.loads(kb_file.read_text(encoding="utf-8"))
            for d in raw:
                docs.append({
                    "id": d["id"],
                    "title": d["title"],
                    "text": d["text"],
                    "text_en": d.get("text_en") or d["text"],
                })
        except Exception as e:
            logger.warning("知识库语料加载失败: %s", e)

        # FAQ 全量入库（作为独立文档，便于 LLM 拿到结构化问答对）
        for category, faqs in FAQ_DATABASE.items():
            for i, faq in enumerate(faqs):
                docs.append({
                    "id": f"faq-{category}-{i}",
                    "title": faq["q_zh"],
                    "text": f"{faq['q_zh']}\n{faq['a_zh']}",
                    "text_en": f"{faq['q_en']}\n{faq['a_en']}",
                })
        return docs

    # ---------- 索引构建 ----------

    async def _ensure_index(self) -> None:
        if self._index_ready:
            return
        async with self._index_lock:
            if self._index_ready:
                return
            self._docs = self._load_docs()
            self._embed_vectors = await self._try_build_embeddings()
            if self._embed_vectors is not None:
                logger.info("RAG 索引就绪：embedding 模式（%d 篇文档）", len(self._docs))
            else:
                self._bigram_index = self._build_bigram_index()
                logger.info("RAG 索引就绪：bigram 降级模式（%d 篇文档）", len(self._docs))
            self._index_ready = True

    async def _try_build_embeddings(self) -> Optional[List[List[float]]]:
        from .llm import llm_service
        if not llm_service.api_key or not self._docs:
            return None
        texts = [f"{d['title']}\n{d['text']}" for d in self._docs]
        cache_key = hashlib.sha1(
            (self.embed_model + "|" + "|".join(texts)).encode("utf-8")
        ).hexdigest()
        cached = self._read_cache(cache_key)
        if cached is not None:
            logger.info("RAG embedding 命中本地缓存")
            return cached
        vectors = await self._embed(texts)
        if vectors:
            self._write_cache(cache_key, vectors)
            return vectors
        return None

    def _read_cache(self, cache_key: str) -> Optional[List[List[float]]]:
        try:
            if not self._cache_file.exists():
                return None
            payload = json.loads(self._cache_file.read_text(encoding="utf-8"))
            if payload.get("key") == cache_key and payload.get("vectors"):
                return payload["vectors"]
        except Exception as e:
            logger.warning("读取 embedding 缓存失败: %s", e)
        return None

    def _write_cache(self, cache_key: str, vectors: List[List[float]]) -> None:
        try:
            self._cache_file.write_text(
                json.dumps({"key": cache_key, "vectors": vectors}, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            logger.warning("写入 embedding 缓存失败: %s", e)

    async def _embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        """调用 OpenAI 兼容 /embeddings 接口；任何失败都返回 None 走降级"""
        from .llm import llm_service
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{llm_service.base_url}/embeddings",
                    headers=llm_service._get_headers(),
                    json={"model": self.embed_model, "input": texts},
                )
                if resp.status_code != 200:
                    logger.warning("Embedding HTTP %d: %s", resp.status_code, resp.text[:200])
                    return None
                data = resp.json()
                items = sorted(data.get("data") or [], key=lambda x: x.get("index", 0))
                vectors = [it.get("embedding") for it in items]
                if len(vectors) != len(texts) or any(not v for v in vectors):
                    logger.warning("Embedding 返回向量数量不符: %d/%d", len(vectors), len(texts))
                    return None
                return vectors
        except Exception as e:
            logger.warning("Embedding 调用异常: %s", e)
            return None

    # ---------- 检索 ----------

    async def retrieve(
        self, query: str, top_k: int = 3, language: str = "zh"
    ) -> List[Dict[str, Any]]:
        """检索 top_k 篇相关知识文档，返回 [{id,title,text,text_en,score}]"""
        if not query.strip():
            return []
        try:
            await asyncio.wait_for(self._ensure_index(), timeout=30)
        except Exception as e:
            logger.warning("RAG 索引构建超时/失败: %s", e)
            return []
        if not self._docs:
            return []

        # 向量检索（查询向量失败则当场降级 bigram）
        if self._embed_vectors is not None:
            qv = await self._embed([query])
            if qv:
                scored = [
                    (i, _cosine(qv[0], v)) for i, v in enumerate(self._embed_vectors)
                ]
                return self._top(scored, top_k, self.embed_min_score)
            logger.warning("查询 embedding 失败，本次降级 bigram 检索")

        if self._bigram_index is None:
            self._bigram_index = self._build_bigram_index()
        qg = _bigrams(query)
        scored = []
        for i, (title_grams, doc_grams) in enumerate(self._bigram_index):
            score = _coverage(qg, doc_grams, title_grams)
            # 领域知识文档小幅优先：FAQ 短问答对已有专属直答通道（高阈值精确匹配），
            # 检索场景下叙述型长文档对 LLM 上下文/摘录回答信息量更大
            if not self._docs[i]["id"].startswith("faq-"):
                score += 0.05
            scored.append((i, score))
        return self._top(scored, top_k, self.bigram_min_score)

    def _build_bigram_index(self) -> List[Tuple[set, set]]:
        return [
            (_bigrams(d["title"]), _bigrams(f"{d['text']}\n{d['text_en']}"))
            for d in self._docs
        ]

    def _top(
        self, scored: List[Tuple[int, float]], top_k: int, min_score: float
    ) -> List[Dict[str, Any]]:
        scored = [(i, s) for i, s in scored if s >= min_score]
        scored.sort(key=lambda x: x[1], reverse=True)
        results = []
        for i, s in scored[:top_k]:
            d = self._docs[i]
            results.append({**d, "score": round(s, 4)})
        return results

    @property
    def mode(self) -> str:
        """当前检索模式：embedding / bigram / uninitialized（便于状态接口展示）"""
        if not self._index_ready:
            return "uninitialized"
        return "embedding" if self._embed_vectors is not None else "bigram"


# 全局 RAG 服务实例
rag_service = RAGService()
