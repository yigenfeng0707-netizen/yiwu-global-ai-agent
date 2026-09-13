"""RAG 知识库检索与客服回复链路测试"""

import pytest

from app.agents.customer_service_agent import CustomerServiceAgent
from app.services.rag import RAGService


# ==================== FAQ 相似度 ====================

class TestFAQSimilarity:
    def setup_method(self):
        self.agent = CustomerServiceAgent()

    def test_identical_question_high_score(self):
        score = self.agent._calculate_similarity(
            "什么是1039市场采购贸易？", "什么是1039市场采购贸易？"
        )
        assert score > 0.9

    def test_unrelated_question_low_score(self):
        score = self.agent._calculate_similarity(
            "今天天气怎么样", "什么是1039市场采购贸易？"
        )
        assert score < 0.3

    def test_faq_match_exact_question(self):
        match = self.agent._match_faq("什么是1039市场采购贸易？", "出海咨询", "zh")
        assert match is not None
        assert "1039" in match["a_zh"]

    def test_faq_no_match_off_topic(self):
        """偏离预设 FAQ 的问题不应被低阈值误命中（旧版 bug 回归）"""
        match = self.agent._match_faq("帮我写一首关于春天的诗", "日用百货", "zh")
        assert match is None


# ==================== RAG 检索 ====================

class TestRAGService:
    @pytest.mark.asyncio
    async def test_retrieve_bigram_mode(self, monkeypatch):
        """强制 bigram 降级模式下也能检索到相关知识文档"""
        rag = RAGService()

        async def no_embed(texts):
            return None

        monkeypatch.setattr(rag, "_embed", no_embed)
        results = await rag.retrieve("义新欧班列到欧洲要多久？")
        assert len(results) > 0
        assert any("义新欧" in r["text"] for r in results)

    @pytest.mark.asyncio
    async def test_retrieve_faq_corpus(self, monkeypatch):
        """FAQ 已并入知识库语料，可被检索"""
        rag = RAGService()

        async def no_embed(texts):
            return None

        monkeypatch.setattr(rag, "_embed", no_embed)
        results = await rag.retrieve("饰品出口欧盟有什么要求？")
        assert len(results) > 0
        assert any("EN1811" in r["text"] or "镍" in r["text"] for r in results)

    @pytest.mark.asyncio
    async def test_retrieve_empty_query(self):
        rag = RAGService()
        assert await rag.retrieve("   ") == []

    @pytest.mark.asyncio
    async def test_retrieve_score_ordering(self, monkeypatch):
        rag = RAGService()

        async def no_embed(texts):
            return None

        monkeypatch.setattr(rag, "_embed", no_embed)
        results = await rag.retrieve("1039市场采购贸易怎么备案？")
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)


# ==================== 回复链路 ====================

class TestReplyChain:
    def setup_method(self):
        self.agent = CustomerServiceAgent()

    @pytest.mark.asyncio
    async def test_faq_direct_answer_source(self):
        """命中 FAQ 直答时 source=faq"""
        result = await self.agent.execute(message="什么是1039市场采购贸易？", category="出海咨询")
        assert result["reply"]["source"] == "faq"
        assert "1039" in result["reply"]["text"]

    @pytest.mark.asyncio
    async def test_reply_always_has_source(self):
        """任意问题都必须返回 source 标记（LLM 不可用时走 kb/template/fallback）"""
        result = await self.agent.execute(message="请介绍一下义乌的五金工具出口情况")
        assert result["reply"].get("source") in {
            "faq", "rag", "llm", "kb", "template", "fallback",
        }
        assert result["reply"]["text"]

    @pytest.mark.asyncio
    async def test_kb_fallback_not_fake_answer(self, monkeypatch):
        """LLM 不可用时：知识库有命中则摘录资料并如实标注，不再返回通用 unknown 模板"""
        async def no_llm(message, session_id="default", contexts=None, language="zh"):
            return None

        monkeypatch.setattr(self.agent, "_llm_chat", no_llm)
        # 注意：不能用 FAQ 原句（会走 faq 直答），用知识库覆盖的非 FAQ 问题
        result = await self.agent.execute(message="义新欧班列到欧洲的运费大概多少钱？")
        assert result["reply"]["source"] in {"kb", "template"}
        if result["reply"]["source"] == "kb":
            assert "义新欧" in result["reply"]["text"]
            assert result["reply"]["references"]
