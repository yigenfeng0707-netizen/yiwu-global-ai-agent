# 义乌跨境 OPC 知识库（remio 睿妙官方工具）

本目录下的 markdown 文档是**金漪湖论剑 OPC 智能体赛道官方工具 remio 睿妙** 的知识库素材。

## 使用方法（满足"使用官方工具 remio 构建知识库"要求）
1. 打开已安装的 remio 睿妙桌面端。
2. 新建知识库「义乌跨境 OPC 知识库」。
3. 将本目录 `01_*.md` ~ `05_*.md` 全部导入该知识库（拖入或"添加资源"）。
4. 基于该知识库创建一个智能体(aApp)，例如"义乌政策合规官"，并复制其分享链接。
5. 将该 aApp 链接填入报名表的「aApp或skill链接」，并在方案文档中注明"知识库基于 remio 睿妙构建"。

> 说明：本仓库后端 `app/knowledge/remio_kb.py` 会直接加载本目录的 markdown，
> 作为合规/政策/选品 Agent 的检索源；当配置 `REMIO_LIVE_CLI=auto` 且 remio 桌面端在运行时，
> 会**实时通过 remio CLI 语义检索官方知识库**（已验证可用），从而让作品在运行时真实"使用 remio 构建的知识库"。
>
> 一键灌库（需 remio 桌面端运行；国区版加 --cn）：
> ```
> remio --cn create_note --title "1039 市场采购贸易方式" --collection "义乌跨境 OPC 知识库" < 01_1039市场采购贸易政策.md
> remio --cn create_note --title "RCEP 与跨境关税优惠" --collection "义乌跨境 OPC 知识库" < 02_RCEP与关税优惠.md
> remio --cn create_note --title "跨境电商合规与认证" --collection "义乌跨境 OPC 知识库" < 03_跨境合规与认证.md
> remio --cn create_note --title "智能选品方法论" --collection "义乌跨境 OPC 知识库" < 04_智能选品方法论.md
> remio --cn create_note --title "金义新区产业带与落地政策" --collection "义乌跨境 OPC 知识库" < 05_金义新区产业带与落地.md
> ```
