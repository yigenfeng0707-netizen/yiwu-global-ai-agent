# 义乌小商品出海智能体-OPC

[![Version](https://img.shields.io/badge/version-V2.0%20冠军版-gold)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.3+-61dafb)](https://react.dev/)

**YiWu Global AI Agent** — 基于7大AI Agent的跨境电商一站式智能服务平台

> 主参赛赛道：**金漪湖·论剑 2026 智能体 OPC 创新创业大赛 · OPC 智能体赛道**（官方工具 remio 睿妙）。注：作品亦可适配"直通乌镇"等 OPC 相关赛事，请以金漪湖·论剑 OPC 智能体赛道要求为准。

## 项目简介

义乌小商品出海智能体-OPC 是一款面向跨境电商的AI智能服务平台，依托义乌小商品城7.5万商户、210万+SKU的产业资源，集成7大AI Agent（市场洞察、智能选品、供应链匹配、跨境内容生成、合规助手、智能客服、政策复制），为中小企业提供从市场分析到商品出海的全链路AI服务，助力义乌发展经验向全国39个市场采购贸易试点城市复制推广。

## 核心亮点

- **7大AI Agent全链路覆盖** — 市场洞察→智能选品→供应链匹配→内容生成→合规查询→智能客服→政策复制，一站式解决跨境电商全流程需求
- **义乌发展经验国家战略** — 习近平总书记多次批示"义乌发展经验"，1039市场采购贸易模式已上升为国家战略
- **39城复制推广** — 1039模式已在全国39个城市试点，义乌经验可复制、可推广
- **OPC模式创新** — Online Platform + City Network，线上平台+城市网络的"义乌经验数字化"模式
- **金漪湖赛道合规：remio 睿妙官方工具** — 知识库基于赛道官方工具 remio 睿妙构建（见 `app/knowledge/remio_export/`），合规/政策/选品 Agent 优先检索 remio 知识
- **智能体自主性 / 工具调用** — 新增「竞品实采」能力（`app/tools/competitor_research.py`），智能体可像人一样**自主打开 Amazon/1688 真实网站**搜索、抽取竞品价格与评论，满足 OPC 智能体赛道对"工具调用与自主性"的评分要求

## 7大AI Agent介绍

| Agent | 名称 | 功能 | 核心能力 |
|-------|------|------|----------|
| 🔍 Market Insight | 市场洞察 | 全球市场趋势分析 | 义乌指数解读、6大区域市场分析、品类趋势预测 |
| 🎯 Smart Selection | 智能选品 | 多维度选品推荐 | 竞争度评分、利润空间分析、义乌优势匹配 |
| 🔗 Supply Chain | 供应链匹配 | 商铺与物流匹配 | 7.5万商铺智能匹配、义新欧班列物流、1039模式对接 |
| ✍️ Content Generation | 跨境内容生成 | 多语言营销内容 | 8语言4平台、SEO关键词、社媒文案、广告素材 |
| 🛡️ Compliance | 合规助手 | 合规与关税查询 | 5国合规要求、1039通关、RCEP优惠、关税计算 |
| 💬 Customer Service | 智能客服 | 多语言智能客服 | 7×24小时、情绪识别、多轮对话、FAQ自动应答 |
| 🏛️ Policy Replication | 政策复制 | 1039政策推广 | 39城试点信息、政策解读、红利计算、成功案例 |
| 🕸️ Competitor Research | 竞品实采 | 真实网站自主调研 | 浏览器自主操作 Amazon/1688，抽取竞品价格/评分/评论 |

## 技术栈

### 后端
- **FastAPI** — 高性能异步API框架
- **LangGraph** — AI Agent编排与工作流引擎
- **Pydantic** — 数据校验与序列化
- **Uvicorn** — ASGI服务器
- **Playwright / WebRetriever** — 竞品实采的浏览器自主操作（智能体自主性）

### 前端
- **React 18** — 用户界面框架
- **TailwindCSS** — 原子化CSS框架
- **Recharts** — 数据可视化

### 知识库（赛道官方工具）
- **remio 睿妙** — 合规/政策/选品知识库基于 remio 构建（`app/knowledge/remio_export/` 为导入素材）

## 快速开始

### 环境要求
- Python 3.12+
- Node.js 18+
- npm 9+

### 后端启动
```bash
cd demo
pip install -r requirements.txt
cp .env.example .env   # 按需填入 LLM_API_KEY 等
python -m app.main      # 或: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 竞品实采（自主性）说明
- 默认 `COMPETITOR_RESEARCH_ENABLED=true`，接口返回真实数据（若环境有浏览器/WebRetriever）或带明确标识的模拟数据。
- 启用真实浏览器调研：安装 `playwright` 后执行 `playwright install chromium`，并设置 `ENABLE_LIVE_COMPETITOR=1`。
- 复用本地最强自主性：将 `webretriever-agent` 目录加入 `PYTHONPATH`，工具会自动优先调用。

### remio 知识库（官方工具）说明
- 将 `app/knowledge/remio_export/` 下 `01_*.md`~`05_*.md` 导入 remio 睿妙桌面端建库；
- 合规/政策/选品 Agent 会优先检索这些知识（见 `app/knowledge/remio_kb.py`）；
- 后端配置 `REMIO_LIVE_CLI=auto` 时，remio 桌面端在运行会**实时通过 remio CLI 语义检索**官方知识库（已实测命中）。

### 已发布的 remio aApp（金漪湖赛道交付物 · v2）
- aApp 名称：**义乌小商品出海助手**（aApp ID：`yiwu-opc-assistant`）
- 市场包：`https://storage.googleapis.com/remio_aapp_market_prod/yiwu-opc-assistant/yiwu-opc-assistant-v3.zip`
- 用法：在 remio 桌面端「aApps / 应用市场」搜索「义乌小商品出海助手」打开。
- **核心能力（直击赛道"工具调用与自主性"评分点）**：
  - `POST /competitor-research` — 智能体**自主调用无头浏览器（`headless_fetch_content`）真实抓取 Amazon / AliExpress / 1688 竞品页面**，再用 LLM 提炼价格/卖点/差异化/选品建议；
  - `POST /ask` — 基于 remio 知识库（义乌跨境 OPC 知识库）流式问答，带引用；
  - `POST /select-product`、`POST /compliance-check`、`POST /policy-replicate` — 多端点编排的选品/合规/政策复制能力。
- 知识底座为 `app/knowledge/remio_export/` 的 5 篇笔记（1039 政策 / RCEP 关税 / 跨境合规 / 智能选品 / 金义新区落地），满足赛道"使用官方工具 remio 构建知识库 + 提供 aApp 链接"的硬性要求。
- 源码归档见 `remio-aapp/yiwu-opc-assistant/`。

### 前端启动
```bash
cd demo/web
npm install
npm run dev
```

### 容器化运行（评委可直跑 Demo）
```bash
cp .env.example .env   # 填入 LLM_API_KEY
docker compose up --build   # 启动 FastAPI 后端 :8000
```
详见 `docs/演示脚本与录屏指南.md`、`docs/架构设计.md`、`docs/商业计划书.md`、`docs/金义新区落地方案.md`、`docs/路演PPT大纲.md`、`docs/自评与改进.md`。

### Demo 实录（API 驱动，无需录屏）
- `scripts/demo_capture.py`：通过 `remio --cn` CLI 重放 aApp 所用的同一组 syscall（rag / headless_fetch_content / run_prompt），真实捕获知识库问答（带引用）与竞品实采（真实无头浏览器抓取）输出。
- `demo_api_transcript.md`：自动生成的演示实录，可作为演示证据直接提交（亦可后续转视频）。
- `demo_video.mp4`：由实录渲染的演示视频（PIL + ffmpeg，约 3 分钟，完整展示真实抓取数据），`scripts/make_demo_video.py` 可重生成。
- `demo_video_narrated.mp4`：含离线中文配音的精修演示版（约 4 分钟，`scripts/make_polished.py` 生成），新增**竞品价格高亮大字卡**、片头淡入动画、轻背景音乐，逐页展示真实竞品价格/评分/来源（Windows Speech TTS，无需联网）。
- `demo_video_short.mp4`：60 秒社媒短版（约 54 秒，片头 + 价格大字卡 + 竞品/选品要点 + 片尾），适合短视频平台传播。

## API 概览（节选）

| 分组 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 市场洞察 | `/api/v1/market-insight` | GET | 市场洞察分析 |
| 竞品实采 | `/api/v1/competitor-research` | GET/POST | 真实网站自主竞品调研 |
| 智能选品 | `/api/v1/smart-selection` | GET | 智能选品推荐 |
| 合规查询 | `/api/v1/compliance` | GET | 合规查询 |
| 政策复制 | `/api/v1/policy-replication/cities` | GET | 39城试点列表 |

详见 `docs/` 下技术文档、商业计划书、路演PPT等参赛材料。
