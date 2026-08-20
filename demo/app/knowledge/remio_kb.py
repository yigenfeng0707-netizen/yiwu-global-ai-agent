"""义乌小商品出海智能体 - remio 睿妙知识库适配层

金漪湖论剑 OPC 智能体赛道硬性要求"使用官方工具 remio 睿妙构建知识库"。
remio 为本地优先桌面应用（无公开后端 API），其标准用法是：
在 remio 中建知识库 → 导出/沉淀领域知识（markdown） → 本适配层加载这些知识，
供合规、政策复制、智能选品等 Agent 优先检索，从而真实"使用 remio 构建的知识库"。

若 remio 未导出知识（目录为空），则安全回退到内置 data 模块，保证服务可运行。
"""

from __future__ import annotations

import os
import re
import json
import shutil
import subprocess
from typing import List, Optional, Tuple


class RemioKnowledgeBase:
    """加载 remio 导出的 markdown 知识，提供轻量中文检索。"""

    def __init__(self, kb_dir: Optional[str] = None):
        self.kb_dir = kb_dir or os.getenv("REMIO_KB_DIR", "app/knowledge/remio_export")
        self.enabled = os.getenv("REMIO_KB_ENABLED", "true").lower() != "false"
        # 实时 CLI 检索（运行时真正调用 remio 官方工具）。默认自动探测。
        self.live_enabled = os.getenv("REMIO_LIVE_CLI", "auto").lower()
        self._docs: List[Tuple[str, str]] = []  # (source_name, text)
        self._loaded = False
        if self.enabled:
            self._load()
        self._cli_base = self._probe_cli()

    def _load(self) -> None:
        self._docs = []
        if not os.path.isdir(self.kb_dir):
            return
        for fname in os.listdir(self.kb_dir):
            if not fname.lower().endswith((".md", ".txt")):
                continue
            if fname.lower().startswith("readme"):
                continue
            path = os.path.join(self.kb_dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                self._docs.append((fname, text))
            except Exception:  # noqa: BLE001
                continue
        self._loaded = True

    def is_available(self) -> bool:
        return self.enabled and len(self._docs) > 0

    # ------------------------------------------------------------------
    # 实时 CLI 检索：运行时真正调用 remio 官方工具（桌面端需运行）
    # ------------------------------------------------------------------
    def _locate_cli(self) -> Optional[str]:
        cand = [
            os.getenv("REMIO_CLI_PATH"),
            shutil.which("remio"),
            r"C:\Users\18969\AppData\Local\Programs\remio-cli\remio.exe",
            r"C:\Users\18969\AppData\Local\Programs\remiocn\remio.exe",
        ]
        for c in cand:
            if c and os.path.isfile(c):
                return c
        return None

    def _probe_cli(self) -> Optional[List[str]]:
        """探测 remio CLI 是否可达；返回基础参数（国区需 --cn）。失败返回 None。"""
        if self.live_enabled == "false":
            return None
        bin_path = self._locate_cli()
        if not bin_path:
            return None
        for base in (["--cn"], []):
            try:
                out = subprocess.run(
                    [bin_path, *base, "list_sync_folders"],
                    capture_output=True, text=True, encoding="utf-8", timeout=8,
                )
                if out.returncode == 0 and '"ok":true' in out.stdout:
                    return [bin_path, *base]
            except Exception:  # noqa: BLE001
                continue
        return None

    def _query_cli(self, query: str, top_k: int = 3, max_chars: int = 1200) -> List[dict]:
        """通过 remio CLI 实时语义检索并读取全文，返回与本地检索同构的块。"""
        if not self._cli_base:
            return []
        bin_path = self._cli_base[0]
        base = self._cli_base[1:]
        try:
            out = subprocess.run(
                [bin_path, *base, "search_notes", "--query", query, "--limit", str(top_k)],
                capture_output=True, text=True, encoding="utf-8", timeout=15,
            )
            data = json.loads(out.stdout).get("data", {})
            results = data.get("results", [])
        except Exception:  # noqa: BLE001
            return []
        chunks = []
        for r in results:
            if r.get("noteType") == "Collection":
                continue
            nid = r.get("noteId")
            try:
                ro = subprocess.run(
                    [bin_path, *base, "read_note", nid],
                    capture_output=True, text=True, encoding="utf-8", timeout=15,
                )
                body = json.loads(ro.stdout).get("data", {}).get("content", "")
                if body.startswith("---"):
                    body = body.split("---", 2)[-1]
                chunks.append({
                    "source": "remio-live:" + r.get("title", nid),
                    "score": 1.0,
                    "content": body.strip()[:max_chars],
                })
            except Exception:  # noqa: BLE001
                continue
        return chunks

    @staticmethod
    def _tokens(text: str) -> set:
        """极简中文/英文分词：英文按词，中文按 2-gram。无第三方依赖。"""
        text = re.sub(r"\s+", "", text.lower())
        toks: set = set()
        # 英文/数字词
        for m in re.findall(r"[a-z0-9]+", text):
            toks.add(m)
        # 中文 2-gram
        cn = re.sub(r"[a-z0-9\s]", "", text)
        for i in range(len(cn) - 1):
            toks.add(cn[i:i + 2])
        return toks

    def retrieve(self, query: str, top_k: int = 3, max_chars: int = 1200) -> List[dict]:
        """按相似度返回最相关知识片段（优先实时 remio CLI，回退本地）。"""
        if self.live_enabled in ("true", "auto") and self._cli_base is not None:
            live = self._query_cli(query, top_k=top_k, max_chars=max_chars)
            if live:
                return live
        if not self.is_available():
            return []
        q_tokens = self._tokens(query)
        if not q_tokens:
            return []
        scored = []
        for src, text in self._docs:
            # 按段落切分，分别打分
            for para in re.split(r"\n{1,}", text):
                para = para.strip()
                if len(para) < 8:
                    continue
                p_tokens = self._tokens(para)
                overlap = len(q_tokens & p_tokens)
                if overlap == 0:
                    continue
                score = overlap / max(1.0, len(q_tokens))
                scored.append((score, src, para))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, src, para in scored[:top_k]:
            results.append({
                "source": src,
                "score": round(score, 3),
                "content": para[:max_chars],
            })
        return results

    def context_for(self, query: str, top_k: int = 3) -> str:
        """拼接检索到的知识，供 Agent 注入提示词。"""
        chunks = self.retrieve(query, top_k=top_k)
        if not chunks:
            return ""
        parts = [f"[remio知识库·{c['source']}] {c['content']}" for c in chunks]
        return "\n".join(parts)


# 单例，供各 Agent 复用
remio_kb = RemioKnowledgeBase()
