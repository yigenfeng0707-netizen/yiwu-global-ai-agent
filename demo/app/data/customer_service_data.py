"""义乌小商品出海智能体 - 客服数据模块"""

# FAQ数据库（按品类）
FAQ_DATABASE = {
    "日用百货": [
        {"q_zh": "日用百货的MOQ是多少？", "a_zh": "义乌日用百货MOQ灵活，一般1-5箱起订，支持混批。1039模式下单票货值15万美元以下可简化申报。", "q_en": "What is the MOQ for daily necessities?", "a_en": "Flexible MOQ from 1-5 cartons, mixed batches supported. Under 1039 mode, simplified declaration for shipments under $150,000."},
        {"q_zh": "日用百货运输到欧洲需要多久？", "a_zh": "义新欧班列14-21天直达欧洲，海运28-35天。建议优先选择义新欧班列，时效快且成本适中。", "q_en": "How long does shipping to Europe take?", "a_en": "Yixinou Railway 14-21 days direct to Europe, sea freight 28-35 days. Yixinou Railway recommended for faster delivery."},
        {"q_zh": "食品接触材料需要什么认证？", "a_zh": "出口欧盟需符合EC 1935/2004，出口美国需FDA认证，出口中东需符合当地食品安全标准。", "q_en": "What certifications are needed for food contact materials?", "a_en": "EU: EC 1935/2004, US: FDA certification, Middle East: local food safety standards."},
    ],
    "饰品配件": [
        {"q_zh": "饰品出口欧盟有什么要求？", "a_zh": "需符合镍释放量标准EN1811，铅镉含量限制REACH附录17，需CE标志。义乌饰品城有专业检测机构。", "q_en": "What are the EU requirements for jewelry?", "a_en": "Must comply with nickel release EN1811, lead/cadmium limits REACH Annex 17, CE marking required."},
        {"q_zh": "饰品可以小批量采购吗？", "a_zh": "可以！义乌饰品城支持小批量混批，最低起订量低至几十件。适合试单和小卖家。", "q_en": "Can I purchase jewelry in small batches?", "a_en": "Yes! Yiwu Jewelry Market supports small mixed batches, MOQ as low as dozens of pieces."},
    ],
    "玩具": [
        {"q_zh": "玩具出口需要什么认证？", "a_zh": "出口欧盟需CE认证+EN71测试，出口美国需ASTM F963，出口中东需SABER认证。义乌有专业认证服务机构。", "q_en": "What certifications are needed for toy exports?", "a_en": "EU: CE + EN71, US: ASTM F963, Middle East: SABER certification. Professional certification services available in Yiwu."},
        {"q_zh": "圣诞用品什么时候开始备货？", "a_zh": "建议3-5月下单，6-8月生产，9-10月发货，确保11月前到达目标市场。义乌圣诞用品占全球出口80%。", "q_en": "When should I start stocking Christmas supplies?", "a_en": "Order Mar-May, produce Jun-Aug, ship Sep-Oct. Yiwu accounts for 80% of global Christmas exports."},
    ],
    "文具办公用品": [
        {"q_zh": "文具出口需要什么认证？", "a_zh": "学生用品需符合EN71安全标准，墨水需无毒认证。出口美国需LHAMA认证。义乌文具专区品类齐全。", "q_en": "What certifications are needed for stationery?", "a_en": "Student supplies: EN71 safety standards, non-toxic ink certification. US: LHAMA certification."},
        {"q_zh": "文具可以OEM定制吗？", "a_zh": "可以！义乌文具供应商支持OEM/ODM定制，包括品牌LOGO、包装设计等。MOQ根据产品不同有所差异。", "q_en": "Can stationery be OEM customized?", "a_en": "Yes! Yiwu suppliers support OEM/ODM customization including brand logo and packaging design."},
    ],
    "针织品": [
        {"q_zh": "袜子MOQ是多少？", "a_zh": "义乌袜子MOQ灵活，一般500-1000双起订，支持混色混码。部分供应商支持更低MOQ。", "q_en": "What is the MOQ for socks?", "a_en": "Flexible MOQ from 500-1000 pairs, mixed colors and sizes supported. Some suppliers offer lower MOQ."},
        {"q_zh": "针织品出口欧洲需要什么认证？", "a_zh": "需符合纺织品标签法规EU 1007/2011，部分需Oeko-Tex认证。建议提前做好认证规划。", "q_en": "What certifications are needed for knitwear to Europe?", "a_en": "EU textile labeling regulation EU 1007/2011, some need Oeko-Tex certification."},
    ],
    "工艺品": [
        {"q_zh": "仿真花出口需要什么认证？", "a_zh": "仿真花一般无需特殊认证，但需符合目标国阻燃标准。含电池产品需电池指令合规。", "q_en": "What certifications are needed for artificial flowers?", "a_en": "Generally no special certification, but must meet flame retardant standards. Battery products need battery directive compliance."},
        {"q_zh": "圣诞用品如何通过义新欧班列运输？", "a_zh": "义乌是义新欧班列始发站，可直接在义乌保税物流中心装箱发运。建议提前1个月预订舱位。", "q_en": "How to ship Christmas supplies via Yixinou Railway?", "a_en": "Yiwu is the departure station. Load at Yiwu Bonded Logistics Center. Book space 1 month in advance."},
    ],
    "电子电器": [
        {"q_zh": "LED灯饰出口需要什么认证？", "a_zh": "出口欧盟需CE+RoHS认证，出口EAEU需EAC认证，出口沙特需SABER认证。义乌有专业检测机构。", "q_en": "What certifications are needed for LED lighting?", "a_en": "EU: CE + RoHS, EAEU: EAC, Saudi Arabia: SABER. Professional testing available in Yiwu."},
        {"q_zh": "小家电出口有什么注意事项？", "a_zh": "需符合EMC和LVD指令，插头需适配目标国标准。建议选择有认证经验的供应商。", "q_en": "What should I note for small appliance exports?", "a_en": "Must comply with EMC and LVD directives, plug adapters for target country standards."},
    ],
    "五金工具": [
        {"q_zh": "手动工具出口需要什么认证？", "a_zh": "出口欧盟需符合EN标准，出口EAEU需EAC认证。一般贸易和1039模式均可出口。", "q_en": "What certifications are needed for hand tools?", "a_en": "EU: EN standards, EAEU: EAC certification. Both general trade and 1039 mode available."},
        {"q_zh": "五金工具在中亚市场前景如何？", "a_zh": "中亚市场基建需求旺盛，五金工具需求持续增长。义新欧班列7天直达阿拉木图，物流优势明显。", "q_en": "How is the hardware tools market in Central Asia?", "a_en": "Strong infrastructure demand, continuous growth. Yixinou Railway reaches Almaty in 7 days."},
    ],
    "服装服饰": [
        {"q_zh": "服装出口需要什么认证？", "a_zh": "需符合纺织品标签法规，儿童服装需EN14682安全标准，羽绒产品需IDFB认证。", "q_en": "What certifications are needed for clothing?", "a_en": "Textile labeling regulations, children's clothing: EN14682, down products: IDFB certification."},
        {"q_zh": "快时尚供应链有什么优势？", "a_zh": "义乌服装供应链小批量快反，7-15天可完成打样到出货。紧跟国际潮流，款式更新快。", "q_en": "What are the advantages of fast fashion supply chain?", "a_en": "Small batch quick response, 7-15 days from sampling to shipping. Trend-following, fast style updates."},
    ],
    "家居装饰": [
        {"q_zh": "灯饰出口需要什么认证？", "a_zh": "出口欧盟需CE认证，出口美国需UL/ETL认证，出口中东需SABER认证。义乌灯饰品类丰富。", "q_en": "What certifications are needed for lighting?", "a_en": "EU: CE, US: UL/ETL, Middle East: SABER. Wide variety of lighting available in Yiwu."},
        {"q_zh": "地毯出口需要什么测试？", "a_zh": "需符合目标国阻燃测试标准，欧盟EN13501-1，美国NFPA标准。部分市场需VOC释放量检测。", "q_en": "What tests are needed for carpet exports?", "a_en": "Flame retardant testing: EU EN13501-1, US NFPA standards. Some markets need VOC emission testing."},
    ],
    "出海咨询": [
        {"q_zh": "什么是1039市场采购贸易？", "a_zh": "1039市场采购贸易是在经认定的市场集聚区采购商品，单票报关单货值15万美元以下，可简化申报、免征增值税。义乌是全国首批试点城市。", "q_en": "What is 1039 market purchase trade?", "a_en": "Market purchase trade allows simplified declaration and VAT exemption for goods under $150,000 purchased in designated market clusters. Yiwu is a pilot city."},
        {"q_zh": "义新欧班列有哪些路线？", "a_zh": "义新欧班列已开通19条线路，覆盖50多个国家160多个城市。主要路线包括义乌-马德里、义乌-伦敦、义乌-德黑兰、义乌-阿拉木图等。", "q_en": "What routes does Yixinou Railway have?", "a_en": "19 routes covering 50+ countries and 160+ cities. Main routes: Yiwu-Madrid, Yiwu-London, Yiwu-Tehran, Yiwu-Almaty."},
        {"q_zh": "义乌国际商贸城有多大？", "a_zh": "义乌国际商贸城拥有7.5万商户、210万+SKU，日均客流量20万人次，是全球最大的小商品批发市场。", "q_en": "How large is Yiwu International Trade City?", "a_en": "75,000 shops, 2.1M+ SKUs, 200,000 daily visitors. The world's largest small commodity wholesale market."},
        {"q_zh": "如何开始义乌小商品跨境出口？", "a_zh": "步骤：1)在义乌市场选品采购 2)办理1039市场采购贸易备案 3)选择物流方式(义新欧班列/海运) 4)办理出口报关 5)目标市场清关配送。我们提供全流程AI辅助。", "q_en": "How to start Yiwu cross-border export?", "a_en": "Steps: 1) Source in Yiwu market 2) Register for 1039 trade 3) Choose logistics 4) Export customs 5) Destination clearance. We provide full-process AI assistance."},
    ],
}

# 情绪类型
EMOTION_TYPES = [
    {"type": "neutral", "label": "中性", "color": "#9ca3af"},
    {"type": "positive", "label": "积极", "color": "#00C9A7"},
    {"type": "negative", "label": "消极", "color": "#ef4444"},
    {"type": "urgent", "label": "紧急", "color": "#f59e0b"},
    {"type": "confused", "label": "困惑", "color": "#8b5cf6"},
]

# 纠纷类型
DISPUTE_TYPES = [
    "质量问题",
    "物流延误",
    "货物损坏",
    "数量不符",
    "认证问题",
    "清关问题",
    "付款争议",
]

# 纠纷关键词
DISPUTE_KEYWORDS = [
    "破损", "损坏", "质量问题", "退货", "退款", "赔偿",
    "延误", "延迟", "未收到", "丢失", "少件", "缺货",
    "认证不过", "清关失败", "被扣", "罚款",
    "不付款", "拖欠", "拒付", "争议",
]

# 自动回复模板
AUTO_REPLY_TEMPLATES = {
    "greeting": "您好！我是义乌小商品出海智能客服，很高兴为您服务。请问有什么可以帮助您的？",
    "unknown": "抱歉，我暂时无法回答这个问题。建议您联系义乌国际商贸城客服热线：0579-85560000，或访问义乌购(yiwugo.com)获取更多信息。",
    "dispute_detected": "检测到您可能遇到了贸易纠纷，建议您：1)保留相关证据 2)联系供应商协商 3)必要时向义乌市商务局投诉。我可以帮您查询相关流程。",
    "logistics_inquiry": "关于物流问题，义新欧班列提供义乌到欧洲/中亚/中东的铁路运输服务，您可以通过义乌保税物流中心(b型)办理发运。海运可从宁波港出发。",
    "certification_inquiry": "关于认证问题，义乌市场内有多个认证服务机构，可以协助办理CE/EAC/SABER等认证。建议提前规划认证周期(一般4-8周)。",
}
