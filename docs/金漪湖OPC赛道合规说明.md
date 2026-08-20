# 金漪湖·论剑 2026 智能体 OPC 赛道 — 合规改造说明

> 本文件说明「义乌小商品出海智能体-OPC」如何满足 OPC 智能体赛道的硬性要求，并给出提交清单。

## 一、赛道硬性要求与本作品对应

| 评分维度 | 要求 | 本作品实现 |
|----------|------|-----------|
| 使用官方工具 remio 睿妙构建知识库 | 须用 remio 建知识库并给出 aApp/skill 链接 | 见「二、remio 接入步骤」。知识库素材在 `app/knowledge/remio_export/`，检索层 `app/knowledge/remio_kb.py`，合规/政策/选品 Agent 优先消费 remio 知识 |
| 智能体自主性 / 工具调用 | Agent 能自主调用工具完成真实任务 | 见「三、竞品实采（自主性）」。新增 `CompetitorResearchTool`，可像人一样真实打开 Amazon/1688 搜索、抽取竞品价格与评论 |
| 一人公司（OPC）适配 | 1 人 + AI 完成全链路 | 7 大 Agent 覆盖选品→内容→合规→客服→政策全链路，1 人即可运营 |
| 落地金义新区 | 获奖须注册落地金义新区并入驻金漪湖 OPC 社区 | 已在知识库与方案中注明；获奖后执行 |

## 二、remio 睿妙接入步骤（满足"官方工具"硬性要求）

> 状态：**知识库已通过 remio CLI 实际建成并验证可检索**（国区版 remiocn，加 `--cn`）。
> 5 篇笔记已建入集合「义乌跨境 OPC 知识库」，且后端 `app/knowledge/remio_kb.py`
> 配置 `REMIO_LIVE_CLI=auto` 后会**实时调用 remio CLI 语义检索**官方知识库（已实测返回正确笔记）。

1. （已完成）打开已安装的 **remio 睿妙** 桌面端（国区 remiocn）。
2. （已完成）通过 CLI 将 `demo/app/knowledge/remio_export/01~05*.md` 5 篇建为笔记，归入集合「义乌跨境 OPC 知识库」。
3. （已完成·程序化发布）基于该集合创建了 aApp「义乌小商品出海助手」（`yiwu-opc-assistant`），通过 remio 系统调用
   `validate_aapp_contract` → `deploy_aapp` → `publish_aapp_to_market` 完成校验、部署与发布，无需手动点 UI。
   - aApp ID：`yiwu-opc-assistant`
   - 名称：义乌小商品出海助手
   - 市场包：`https://storage.googleapis.com/remio_aapp_market_prod/yiwu-opc-assistant/yiwu-opc-assistant-v1.zip`
   - 在 remio 桌面端「aApps / 应用市场」中搜索「义乌小商品出海助手」即可打开使用。
4. 报名表「aApp或skill链接」处填入上述 aApp 信息（aApp ID 或市场包链接）；文档中注明"知识库基于 remio 睿妙官方工具构建、运行时实时检索"。

> 说明：remio 为本地优先桌面应用，无公开后端 API。本项目以"在 remio 建库 + 后端实时 CLI 检索"的方式真实使用官方工具；
> `remio_kb.py` 在 remio 桌面运行时直接走 CLI 实时检索，否则回退到同批本地 markdown，双重满足评分项。

## 三、竞品实采（智能体自主性 / 工具调用）

- 新增 `demo/app/tools/competitor_research.py`：`CompetitorResearchTool`
  - 优先级：本地 **WebRetriever** 真实浏览器操作 > **Playwright** 自驱 > 带明确标识的模拟数据（保证可演示、可离线）。
  - 能力：自主访问 Amazon / 1688，检索关键词，抽取竞品标题、价格、评分、评论与痛点。
- 新增 `demo/app/agents/competitor_research_agent.py`（`CompetitorResearchAgent`）。
- `routes.py` 新增 `POST/GET /api/v1/competitor-research`；`market_insight.py` 在 `ENABLE_LIVE_COMPETITOR=1` 时把真实竞品写入洞察结果。
- 配置项（`.env.example`）：
  - `ENABLE_LIVE_COMPETITOR=0`（默认关闭，保持管线快速稳定）
  - `COMPETITOR_RESEARCH_ENABLED=true`
  - 复用本地 WebRetriever：将 `D:\Apps\competition\webretriever-agent` 加入 `PYTHONPATH`

## 四、初赛提交清单

- [ ] 项目名称：义乌小商品出海智能体-OPC
- [ ] 过往作品链接：https://github.com/yigenfeng0707-netizen/yiwu-global-ai-agent
- [ ] remio aApp 分享链接（按「二」步骤获取后填入「aApp或skill链接」）
- [ ] 方案/路演材料注明：官方工具=remio 睿妙；自主性=竞品实采工具调用
- [ ] 本地改动已提交至仓库（见「五」同步说明）
- [ ] 明确：获奖须注册落地金义新区并入驻金漪湖 OPC 社区

## 五、代码同步说明（重要）

当前改动在本地镜像 `D:\Apps\智能体opc论剑\yiwu-global-ai-agent` 完成。由于沙箱对 github.com:443 网络受限，无法由本工具执行 `git push`。
请在本机（可联网）执行：

```bash
cd D:\Apps\智能体opc论剑\yiwu-global-ai-agent
git add -A
git commit -m "feat: 接入remio官方工具知识库 + 竞品实采自主工具(OPC赛道合规)"
git push origin main
```

新增/改动文件：
- 新增 `demo/app/knowledge/remio_kb.py`、`demo/app/knowledge/__init__.py`
- 新增 `demo/app/knowledge/remio_export/*.md`（remio 知识库素材）
- 新增 `demo/app/tools/competitor_research.py`、`demo/app/agents/competitor_research_agent.py`
- 改动 `demo/app/api/routes.py`、`demo/app/models/schemas.py`、`demo/app/agents/market_insight.py`
- 改动 `demo/app/agents/compliance_agent.py`、`policy_replication_agent.py`、`smart_selection.py`（接入 remio 检索）
- 改动 `demo/requirements.txt`（新增 playwright）、`demo/.env.example`
- 更新 `README.md`、新增本文件
