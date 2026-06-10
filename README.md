# 义乌小商品出海智能体-OPC

[![Version](https://img.shields.io/badge/version-V2.0%20冠军版-gold)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.3+-61dafb)](https://react.dev/)

**YiWu Global AI Agent** — 基于7大AI Agent的跨境电商一站式智能服务平台

> 参赛赛道：2026"直通乌镇"全球互联网大赛 OPC特色赛

## 项目简介

义乌小商品出海智能体-OPC 是一款面向跨境电商的AI智能服务平台，依托义乌小商品城7.5万商户、210万+SKU的产业资源，集成7大AI Agent（市场洞察、智能选品、供应链匹配、跨境内容生成、合规助手、智能客服、政策复制），为中小企业提供从市场分析到商品出海的全链路AI服务，助力义乌发展经验向全国39个市场采购贸易试点城市复制推广。

## 核心亮点

- **7大AI Agent全链路覆盖** — 市场洞察→智能选品→供应链匹配→内容生成→合规查询→智能客服→政策复制，一站式解决跨境电商全流程需求
- **义乌发展经验国家战略** — 习近平总书记多次批示"义乌发展经验"，1039市场采购贸易模式已上升为国家战略
- **39城复制推广** — 1039模式已在全国39个城市试点，义乌经验可复制、可推广
- **OPC模式创新** — Online Platform + City Network，线上平台+城市网络的"义乌经验数字化"模式

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

## 义乌独有壁垒

| 壁垒 | 说明 |
|------|------|
| 📊 **义乌指数** | 全球小商品价格风向标，10大品类实时指数，为选品提供数据支撑 |
| 🚂 **义新欧班列** | 19条线路、50国160城直达，比海运快2-3倍、比空运便宜60-80% |
| 📋 **1039模式** | 市场采购贸易方式，增值税免征、简化申报、通关便利化，合规成本降低80% |
| 🏙️ **义乌发展经验** | 国家战略级经验，习近平总书记多次批示，39城复制推广 |

## 技术栈

### 后端
- **FastAPI** — 高性能异步API框架
- **LangGraph** — AI Agent编排与工作流引擎
- **Pydantic** — 数据校验与序列化
- **Uvicorn** — ASGI服务器

### 前端
- **React 18** — 用户界面框架
- **TailwindCSS** — 原子化CSS框架
- **Recharts** — 数据可视化
- **Framer Motion** — 动画库
- **Zustand** — 状态管理

### 数据源
1. **义乌小商品城** — 7.5万商户、210万+SKU实时数据
2. **义新欧班列** — 19条线路、50国160城物流数据
3. **Amazon** — 全球平台销售数据
4. **Alibaba.com** — 国际站B2B数据
5. **行业报告** — 义乌指数及行业研究报告

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- npm 9+

### 后端启动

```bash
# 进入后端目录
cd demo

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要配置

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端启动

```bash
# 进入前端目录
cd demo/web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 访问地址

- 前端：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 项目结构

```
YiWuInternetCompetition/
├── demo/
│   ├── app/                          # 后端应用
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI主应用
│   │   ├── agents/                   # AI Agent模块
│   │   │   ├── base.py               # Agent基类
│   │   │   ├── market_insight.py      # 市场洞察Agent
│   │   │   ├── smart_selection.py     # 智能选品Agent
│   │   │   ├── supply_chain_agent.py  # 供应链匹配Agent
│   │   │   ├── content_generation.py  # 跨境内容生成Agent
│   │   │   ├── compliance_agent.py    # 合规助手Agent
│   │   │   ├── customer_service_agent.py # 智能客服Agent
│   │   │   ├── policy_replication_agent.py # 政策复制Agent
│   │   │   └── workflow.py            # 全链路工作流
│   │   ├── api/
│   │   │   └── routes.py             # API路由
│   │   ├── data/                     # 数据模块
│   │   │   ├── market_data.py        # 市场数据
│   │   │   ├── content_data.py       # 内容数据
│   │   │   ├── compliance_data.py    # 合规数据
│   │   │   ├── customer_service_data.py # 客服数据
│   │   │   ├── policy_data.py        # 政策数据
│   │   │   └── sources.py            # 数据源管理
│   │   ├── middleware/               # 中间件
│   │   │   ├── auth.py               # 认证中间件
│   │   │   ├── rate_limit.py         # 限流中间件
│   │   │   └── signature.py          # 签名中间件
│   │   ├── models/
│   │   │   └── schemas.py            # 数据模型
│   │   └── services/                 # 服务层
│   │       ├── auth.py               # 认证服务
│   │       └── llm.py                # LLM服务
│   ├── web/                          # 前端应用
│   │   ├── src/
│   │   │   ├── App.tsx               # 应用入口
│   │   │   ├── pages/                # 页面组件
│   │   │   │   ├── Home.tsx          # 首页仪表盘
│   │   │   │   ├── MarketInsight.tsx  # 市场洞察
│   │   │   │   ├── SmartSelection.tsx # 智能选品
│   │   │   │   ├── SupplyChain.tsx    # 供应链匹配
│   │   │   │   ├── ContentGeneration.tsx # 内容生成
│   │   │   │   ├── Compliance.tsx     # 合规查询
│   │   │   │   ├── CustomerService.tsx # 智能客服
│   │   │   │   ├── PolicyReplication.tsx # 政策复制
│   │   │   │   ├── Pipeline.tsx       # 全链路工作流
│   │   │   │   ├── Pricing.tsx        # 定价页面
│   │   │   │   └── Login.tsx          # 登录页面
│   │   │   ├── components/           # 通用组件
│   │   │   ├── hooks/                # 自定义Hooks
│   │   │   ├── store/                # 状态管理
│   │   │   └── utils/                # 工具函数
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── tailwind.config.js
│   ├── requirements.txt
│   └── .env.example
├── README.md
└── 用户使用手册.docx
```

## API概览

| 分组 | 端点 | 方法 | 说明 |
|------|------|------|------|
| **基础** | `/api/v1/` | GET | API根路径 |
| | `/api/v1/agents/info` | GET | 获取智能体信息 |
| | `/api/v1/categories` | GET | 获取品类列表 |
| | `/api/v1/regions` | GET | 获取目标市场区域 |
| | `/api/v1/yiwu-index` | GET | 获取义乌指数 |
| **市场洞察** | `/api/v1/market-insight` | GET | 市场洞察分析 |
| **智能选品** | `/api/v1/smart-selection` | GET | 智能选品推荐 |
| **供应链** | `/api/v1/supply-chain/{category}` | GET | 供应链匹配 |
| | `/api/v1/supply-chain` | POST | 供应链匹配(POST) |
| | `/api/v1/logistics/yixinou` | GET | 义新欧班列物流 |
| **内容生成** | `/api/v1/content/generate` | POST | 生成跨境内容 |
| **合规查询** | `/api/v1/compliance` | GET | 合规查询 |
| | `/api/v1/tariff/calculate` | POST | 关税计算 |
| **智能客服** | `/api/v1/customer-service/chat` | POST | 智能客服聊天 |
| | `/api/v1/customer-service/faq` | GET | 获取FAQ |
| **政策复制** | `/api/v1/policy-replication/cities` | GET | 39城试点列表 |
| | `/api/v1/policy-replication/city/{city_name}` | GET | 单城市试点信息 |
| | `/api/v1/policy-replication/policy-guide` | GET | 1039政策解读 |
| | `/api/v1/policy-replication/calculate-benefit` | POST | 政策红利计算 |
| | `/api/v1/policy-replication/cases` | GET | 义乌成功案例 |
| **全链路** | `/api/v1/pipeline` | POST | 全链路工作流 |
| **认证** | `/api/v1/auth/register` | POST | 用户注册 |
| | `/api/v1/auth/login` | POST | 用户登录 |

## 三级增长飞轮

```
┌─────────────────────────────────────────────────────────┐
│                    第三级：城市网络飞轮                      │
│   39城试点 → 义乌经验复制 → 城市合伙人 → 规模效应          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │                第二级：平台生态飞轮                      │ │
│ │   更多商户 → 更丰富数据 → 更精准AI → 更多用户          │ │
│ │ ┌─────────────────────────────────────────────────┐ │ │
│ │ │              第一级：单点突破飞轮                    │ │ │
│ │ │   义乌数据 → AI Agent → 用户价值 → 口碑传播       │ │ │
│ │ └─────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 商业模式

### 4档定价

| 版本 | 价格 | 目标用户 | 核心功能 |
|------|------|----------|----------|
| 免费版 | ¥0/月 | 个人卖家 | 基础市场洞察、3次/日选品 |
| 专业版 | ¥299/月 | 中小企业 | 全部Agent、50次/日、义新欧物流 |
| 企业版 | ¥999/月 | 规模企业 | 无限调用、API接入、专属客服 |
| 旗舰版 | ¥2,999/月 | 大型企业 | 定制Agent、私有部署、数据分析 |

### 政府采购

- 义乌市政府数字贸易平台采购
- 39城商务局市场采购贸易数字化工具
- 一带一路沿线城市跨境电商公共服务平台

### 城市合伙人

- 39城本地化运营合伙人招募
- 城市合伙人享受当地客户收益分成
- 义乌总部提供技术支持与培训

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

### 开发规范

- 后端遵循 PEP 8 代码风格
- 前端遵循 ESLint + TypeScript 规范
- 提交信息遵循 Conventional Commits 规范
- 新功能需包含对应的单元测试

## License

本项目基于 [MIT License](LICENSE) 开源。

## 联系方式

- 项目地址：[GitHub Repository](https://github.com)
- 邮箱：contact@yiwu-global-ai.com
- 参赛团队：义乌小商品出海智能体团队
- 参赛赛道：2026"直通乌镇"全球互联网大赛 OPC特色赛
