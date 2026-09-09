# Yiwu Going-Global AI Agent (OPC)

**One-Person-Company · One AI Team · One Click to the World**

> Empowering 75,000 Yiwu merchants and 2.1 million MSMEs across 39 national market-procurement pilot cities to sell globally — with a team of 7 AI agents replacing the traditional 7-role foreign-trade back office.

**Founder:** Yigen Feng · **Stage:** Seed · **Ask:** CNY 1,000,000 · **Contact:** yigen.feng0707@gmail.com

---

## 1. The Problem

Yiwu — the world's largest small-commodities market — moved **CNY 836.5 billion** in imports and exports in 2025 (+16.2% YoY), more than 12 Chinese provinces. Yet fewer than **15% of its 75,000 merchants** actually sell overseas. The same gap exists across the **39 national market-procurement (1039) pilot cities** and their **2.1 million MSMEs**.

Field research with 300+ Yiwu merchants surfaces five structural blockers:

| # | Blocker | Symptom |
|---|---|---|
| 1 | **Language** | Merchants speak only "hello / how much"; Arabic-, Spanish-, Russian-speaking buyers force calculator-and-gesture selling |
| 2 | **Channels** | Unsure whether to list on Amazon, Temu, TikTok Shop, or find regional distributors |
| 3 | **Compliance** | EU CE / US FDA / GCC Halal requirements unclear; one certification gap kills a quarter's orders |
| 4 | **Operations** | Product pages, keyword strategy, ad buying — merchants make goods, not traffic |
| 5 | **Logistics** | Sea vs air, LCL vs FCL, tariff math, clearance paperwork — one mistake erases margin |

Traditional fixes (translation agencies, freight forwarders, compliance consultants, operations outsourcers) are **expensive, fragmented and slow** — a full foreign-trade back office costs CNY 1M+ per year, out of reach for MSMEs.

## 2. Our Solution — 7 AI Agents, One Orchestrated Pipeline

**OPC** ("One Person Company") turns a single merchant into a full foreign-trade company. Seven LLM-enhanced agents, orchestrated by **LangGraph**, cover the end-to-end going-global workflow:

| Agent | Role it replaces | Core capability |
|---|---|---|
| **Market Insight** | Market analyst | Global demand signals; ingests the **official Yiwu Index** (ywindex.com, published values with source URL + timestamp) |
| **Smart Selection** | Category buyer | Scores 2.1M SKUs by competition × margin × Yiwu supply advantage |
| **Content Generation** | Copywriter + translator | Product pages, ads, short-video scripts in **8 languages** |
| **Compliance Query** | Compliance officer | Maps HS codes to CE/FDA/Halal/RoHS requirements; 3-month cycle compressed to 3 days |
| **Customer Service** | 24/7 support team | Multi-turn chat with emotion + dispute detection, session memory, FAQ grounding |
| **Supply Chain Matching** | Sourcing agent | Buyer intent → top-3 Yiwu suppliers in seconds; 1039 clearance + Yixinou rail linkage |
| **Policy Replication** | Policy researcher | Parses 39-city 1039 policy differences; adapts Yiwu's playbook to each city |

Every agent pairs a **deterministic rule/formula backbone** with **LLM reasoning augmentation**; when no API key is configured, the system gracefully degrades to backbone-only output (flagged via `ai_used=false`) — no silent hallucination.

## 3. Why Now

- **National strategy.** The 1039 market-procurement model, pioneered in Yiwu, has been replicated to **39 pilot cities**. Central leadership has explicitly called for "summarising and applying the Yiwu development experience" — the policy rails are laid.
- **Data rails.** The Yiwu Index (official published values) and daily reference FX rates are now machine-readable; our ETL pipeline ingests both with source URL + timestamp provenance.
- **Model rails.** LLM + RAG + LangGraph multi-agent orchestration matured in 2024–2025, making a "7-role AI team" technically and economically viable for the first time.

## 4. Market Opportunity

| Layer | Size | Basis |
|---|---|---|
| **TAM** | ~CNY 1.5B annual SaaS + services | 2.1M MSMEs × 10% paid conversion × CNY 500/mo avg + 39-city government procurement (~CNY 30M) + transaction commissions |
| **SAM** | ~CNY 450M | Yiwu (75K merchants) + first-wave 10 pilot cities |
| **SOM (Y1–Y3)** | CNY 7M → 120M → 400M revenue | Flywheel 1 (Yiwu) → Flywheel 2 (39 cities) → Flywheel 3 (global network) |

## 5. Business Model — Three Revenue Streams

1. **SaaS subscription** (four tiers):
   - **Yiwu Merchant Exclusive — CNY 199/mo** (flagship, for Yiwu International Trade City tenants: full Pro features + Yiwu-specific data + priority supply-chain matching + 1039 compliance guidance)
   - Basic CNY 299/mo · Pro CNY 999/mo · Enterprise from CNY 50,000/yr
2. **Government procurement.** 39 pilot-city governments buy the platform for local merchants at **CNY 500K–1M per city per year** → addressable CNY 20–40M.
3. **City partners.** 1–2 local partners per city handle merchant onboarding; revenue share on subscriptions and transaction fees.

## 6. Traction (as of Sep 2026)

- **Product live** on ModelScope Studio (public demo URL); full stack containerised (FastAPI + React + SQLite + LangGraph).
- **2 real data sources integrated** with provenance badges in UI:
  - Daily reference FX (open.er-api.com) — verified USD/CNY 6.7284 with official timestamp
  - Yiwu Index official published values (ywindex.com/report) — 9 category indices fetched live (e.g. Umbrella 1576.52, Hardware 1557.03, Composite 1513.01)
- **All 7 agents LLM-enhanced** (DashScope qwen-plus / StepFun in production); SSE-streamed real LangGraph pipeline progress replaces fake setTimeout animations.
- **Engineering quality gates green:** 150 pytest cases pass; flake8 blocking gate (E9/F63/F7/F82) clean; frontend tsc + eslint clean; CI + deploy pipeline with test gate before ModelScope push.
- **API contract enforced:** Pydantic `response_model` on all stable endpoints; enum validation on category/region/budget/language returns HTTP 400 with allowed-value list.
- **Auth loop closed:** JWT issued on login, injected into every `apiFetch`, cleared on 401 / logout.
- **Software copyright** filing prepared; demo videos and pitch deck (CN) delivered.

## 7. Competitive Moats

1. **National-level Yiwu experience.** Deep, on-the-ground understanding of the 1039 model, Yiwu Index semantics and merchant workflows — not open-sourceable, not downloadable.
2. **39-city replication network effect.** Every new city enriches the policy corpus, which sharpens every agent. Later entrants face a data flywheel they cannot bootstrap.
3. **Three resources unique to Yiwu.** The Yiwu Index (global small-commodity price barometer), the Yixinou China–Europe rail express (13 days to Europe), and the 1039 clearance regime — none replicable elsewhere.

## 8. Roadmap — Three Growth Flywheels

- **Flywheel 1 (Yiwu validation, M1–M6).** 1,000 paying merchants, CNY 500K MRR; deepen the 7-agent model, build proprietary Yiwu data assets.
- **Flywheel 2 (39-city replication, M7–M18).** Policy Replication Agent carries the Yiwu playbook to all 39 pilot cities; target 20,000 merchants, CNY 10M MRR.
- **Flywheel 3 (global network, M19+).** From "China-manufacturing going global" to "global small-commodity intelligent matching" — positioning OPC as the digital infrastructure of Chinese trade.

## 9. Financial Snapshot

Authoritative source: internal financial model (`财务预测与商业计划.md`).

| Metric | Y1 target |
|---|---|
| Cumulative revenue | **CNY 6.97M** |
| Cash-flow breakeven | **First month** (OPC model → zero headcount cost for first 6 months) |
| Full-year net margin | **68–72%** (SaaS gross margin + AI-native cost structure) |
| LTV / CAC | Well above industry benchmark (see model) |

## 10. Funding Ask & Use of Proceeds

Seeking **CNY 1,000,000 seed**:

| Use | Share | Amount |
|---|---|---|
| R&D (7-agent depth, 39-city policy corpus) | 40% | CNY 400K |
| Go-to-market (Yiwu ground push, first 1,000 merchants, pilot-city rollout) | 30% | CNY 300K |
| Team (core engineers, operations, policy researchers) | 20% | CNY 200K |
| Operating reserve | 10% | CNY 100K |

## 11. Team

**Yigen Feng — Founder.** Technology + cross-border dual background; deep expertise in LLM applications and AI-agent engineering; hands-on familiarity with the Yiwu merchant ecosystem. Currently recruiting co-founders / partners in cross-border operations, business development and policy research.

**OPC operating principle:** "1 founder + 7 AI digital employees = one complete foreign-trade company." The 7 agents replace 7 traditional roles; part-time engineering collaborators support the founder on infrastructure.

---

*Prepared for the Yiwu Going-Global OPC track · Single source of truth for all numbers: `docs/核心数字基准表.md` · English one-pager generated from the authoritative Chinese business plan.*
