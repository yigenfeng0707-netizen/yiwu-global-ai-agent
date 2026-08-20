---
name: yiwu-opc-assistant
description: 基于 remio 知识库（义乌跨境 OPC 知识库）与真实网页自主抓取的义乌小商品出海智能体，回答 1039 市场采购、RCEP 关税、跨境合规、智能选品、金义新区落地等问题，并自主抓取 Amazon/AliExpress/1688 竞品页面做实采分析。
---

本 aApp 是「义乌小商品出海智能体-OPC」在 remio 中的官方智能体入口（v2）。它既用 remio 官方工具构建的知识库（义乌跨境 OPC 知识库，含 1039 政策 / RCEP 关税 / 跨境合规 / 智能选品 / 金义新区落地 5 篇笔记）做 RAG 问答，也能**自主调用无头浏览器真实抓取电商页面**做竞品实采——直接体现本赛道看重的「工具调用与自主性」。

对应参赛作品「义乌小商品出海智能体-OPC」（https://github.com/yigenfeng0707-netizen/yiwu-global-ai-agent）。

Endpoints:
- `POST /ask` (input*:string) — 基于 remio 知识库流式回答义乌出海相关问题，返回带内联引用的流式内容。
- `POST /competitor-research` (input*:string) — 自主用 headless_fetch_content 抓取 Amazon/AliExpress/1688 真实竞品页，再用 LLM 提炼价格/卖点/差异化/选品建议（工具调用+自主性的核心展示）。
- `POST /select-product` (input?:string) — 基于知识库的智能选品推荐。
- `POST /compliance-check` (input?:string) — 基于知识库的跨境合规与认证检查清单。
- `POST /policy-replicate` (input?:string) — 政策复制与金义新区落地方法论。
- `GET /welcome` — 返回欢迎语与能力说明。

chatMenu 提供：1039 免税、竞品实采、智能选品、合规检查、政策复制与落地 五个快捷入口。
