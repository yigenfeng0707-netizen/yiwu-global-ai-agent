"""义乌小商品出海智能体 - 市场数据模块"""

# 义乌十大核心品类
CATEGORY_LIST = [
    "日用百货",
    "饰品配件",
    "玩具",
    "文具办公用品",
    "针织品",
    "工艺品",
    "电子电器",
    "五金工具",
    "服装服饰",
    "家居装饰",
]

# 目标市场区域
SUPPORTED_REGIONS = [
    "欧洲（义新欧班列直达）",
    "中亚",
    "中东",
    "东南亚",
    "非洲",
    "南美",
]

# 义乌指数数据
YIWU_INDEX = {
    "current": 102.8,
    "change": 1.35,
    "trend": "上涨",
    "categories": {
        "日用百货": 105.2,
        "饰品配件": 101.8,
        "玩具": 108.5,
        "文具办公用品": 99.3,
        "针织品": 103.7,
        "工艺品": 100.5,
        "电子电器": 107.1,
        "五金工具": 98.6,
        "服装服饰": 104.2,
        "家居装饰": 106.8,
    },
}

# 义新欧班列数据
YIXINOU_DATA = {
    "total_routes": 19,
    "countries_covered": 50,
    "cities_connected": 160,
    "annual_trips": 1600,
    "transit_days": {
        "欧洲": 14,
        "中亚": 7,
        "中东": 12,
        "俄罗斯": 10,
    },
    "main_routes": [
        {"name": "义乌-马德里", "days": 21, "frequency": "每周3班"},
        {"name": "义乌-伦敦", "days": 18, "frequency": "每周2班"},
        {"name": "义乌-德黑兰", "days": 14, "frequency": "每周2班"},
        {"name": "义乌-阿拉木图", "days": 7, "frequency": "每周4班"},
        {"name": "义乌-莫斯科", "days": 10, "frequency": "每周3班"},
        {"name": "义乌-明斯克", "days": 12, "frequency": "每周2班"},
    ],
    "cost_per_container": {
        "20ft": "$2800-3500",
        "40ft": "$4200-5500",
    },
}

# 义乌国际商贸城数据
YIWU_TRADE_CITY = {
    "total_shops": 75000,
    "total_skus": 2100000,
    "daily_visitors": 200000,
    "districts": {
        "一区": {"categories": ["玩具", "工艺品"], "shops": 12000},
        "二区": {"categories": ["五金工具", "电子电器"], "shops": 15000},
        "三区": {"categories": ["文具办公用品", "日用百货"], "shops": 13000},
        "四区": {"categories": ["服装服饰", "针织品"], "shops": 14000},
        "五区": {"categories": ["饰品配件", "家居装饰"], "shops": 11000},
    },
}

# 1039市场采购贸易模式
MARKET_PURCHASE_TRADE_1039 = {
    "name": "市场采购贸易方式（1039）",
    "description": "在经认定的市场集聚区采购商品，单票报关单商品货值15万（含）以下，可直接办理出口通关",
    "advantages": [
        "免征增值税，不办理出口退税",
        "简化报关流程，实行简化申报",
        "允许多主体收汇，支持人民币结算",
        "通关便利化，查验率低",
        "适合小商品多品种出口",
    ],
    "conditions": [
        "在义乌市场集聚区内采购",
        "单票货值15万美元以下",
        "在指定口岸出口",
    ],
}

# 各品类市场数据
MARKET_DATA = {
    "日用百货": {
        "market_size": "580亿美元",
        "growth_rate": "12.5%",
        "hot_products": ["厨房用品", "清洁工具", "收纳整理", "一次性用品", "卫浴用品"],
        "avg_price_range": "$0.5-15",
        "yiwu_advantage": "义乌一区、三区集中供应，品类齐全，价格优势明显",
        "yiwu_index_score": 105.2,
        "target_markets": {
            "欧洲（义新欧班列直达）": {"share": "35%", "growth": "15.2%"},
            "中亚": {"share": "25%", "growth": "18.5%"},
            "中东": {"share": "20%", "growth": "22.3%"},
            "东南亚": {"share": "12%", "growth": "10.8%"},
            "非洲": {"share": "5%", "growth": "25.6%"},
            "南美": {"share": "3%", "growth": "14.2%"},
        },
    },
    "饰品配件": {
        "market_size": "320亿美元",
        "growth_rate": "15.8%",
        "hot_products": ["时尚首饰", "发饰", "纽扣拉链", "丝带花边", "珠串配件"],
        "avg_price_range": "$0.1-8",
        "yiwu_advantage": "义乌五区饰品专区，全球最大饰品集散中心",
        "yiwu_index_score": 101.8,
        "target_markets": {
            "欧洲（义新欧班列直达）": {"share": "30%", "growth": "12.5%"},
            "中亚": {"share": "15%", "growth": "20.3%"},
            "中东": {"share": "28%", "growth": "25.1%"},
            "东南亚": {"share": "18%", "growth": "13.7%"},
            "非洲": {"share": "6%", "growth": "30.2%"},
            "南美": {"share": "3%", "growth": "16.8%"},
        },
    },
    "玩具": {
        "market_size": "950亿美元",
        "growth_rate": "8.6%",
        "hot_products": ["益智玩具", "毛绒玩具", "遥控玩具", "水枪水球", "DIY手工"],
        "avg_price_range": "$1-25",
        "yiwu_advantage": "义乌一区玩具城，全球最大玩具批发市场之一",
        "yiwu_index_score": 108.5,
        "target_markets": {
            "欧洲（义新欧班列直达）": {"share": "38%", "growth": "9.5%"},
            "中亚": {"share": "18%", "growth": "15.3%"},
            "中东": {"share": "22%", "growth": "18.7%"},
            "东南亚": {"share": "15%", "growth": "11.2%"},
            "非洲": {"share": "4%", "growth": "22.1%"},
            "南美": {"share": "3%", "growth": "12.5%"},
        },
    },
    "文具办公用品": {
        "market_size": "280亿美元",
        "growth_rate": "6.8%",
        "hot_products": ["笔类", "本册", "办公收纳", "美术用品", "学生文具"],
        "avg_price_range": "$0.2-10",
        "yiwu_advantage": "义乌三区文具专区，品类丰富，价格极具竞争力",
        "yiwu_index_score": 99.3,
        "target_markets": {
            "欧洲（义新欧班列直达）": {"share": "32%", "growth": "5.8%"},
            "中亚": {"share": "22%", "growth": "12.5%"},
            "中东": {"share": "20%", "growth": "10.3%"},
            "东南亚": {"share": "18%", "growth": "8.7%"},
            "非洲": {"share": "5%", "growth": "18.5%"},
            "南美": {"share": "3%", "growth": "9.2%"},
        },
    },
    "针织品": {
        "market_size": "420亿美元",
        "growth_rate": "10.2%",
        "hot_products": ["袜子", "围巾", "帽子", "手套", "毛线"],
        "avg_price_range": "$0.3-12",
        "yiwu_advantage": "义乌四区针织专区，全球最大袜子生产基地",
        "yiwu_index_score": 103.7,
        "target_markets": {
            "欧洲（义新欧班列直达）": {"share": "35%", "growth": "11.5%"},
            "中亚": {"share": "25%", "growth": "16.8%"},
            "中东": {"share": "18%", "growth": "20.3%"},
            "东南亚": {"share": "14%", "growth": "9.5%"},
            "非洲": {"share": "5%", "growth": "28.7%"},
            "南美": {"share": "3%", "growth": "11.2%"},
        },
    },
    "工艺品": {
        "market_size": "260亿美元",
        "growth_rate": "9.5%",
        "hot_products": ["装饰画", "仿真花", "节日用品", "相框", "水晶工艺品"],
        "avg_price_range": "$0.5-20",
        "yiwu_advantage": "义乌一区工艺品专区，圣诞用品占全球出口80%",
        "yiwu_index_score": 100.5,
        "target_markets": {
            "欧洲（义新欧班列直达）": {"share": "42%", "growth": "8.2%"},
            "中亚": {"share": "12%", "growth": "14.5%"},
            "中东": {"share": "15%", "growth": "16.8%"},
            "东南亚": {"share": "18%", "growth": "10.3%"},
            "非洲": {"share": "8%", "growth": "20.5%"},
            "南美": {"share": "5%", "growth": "13.7%"},
        },
    },
    "电子电器": {
        "market_size": "780亿美元",
        "growth_rate": "14.3%",
        "hot_products": ["小家电", "LED灯饰", "手机配件", "电子钟表", "电源适配器"],
        "avg_price_range": "$1-50",
        "yiwu_advantage": "义乌二区电子电器专区，小家电和LED灯饰品类齐全",
        "yiwu_index_score": 107.1,
        "target_markets": {
            "欧洲（义新欧班列直达）": {"share": "30%", "growth": "13.5%"},
            "中亚": {"share": "20%", "growth": "22.8%"},
            "中东": {"share": "25%", "growth": "18.6%"},
            "东南亚": {"share": "16%", "growth": "12.3%"},
            "非洲": {"share": "6%", "growth": "30.5%"},
            "南美": {"share": "3%", "growth": "15.8%"},
        },
    },
    "五金工具": {
        "market_size": "350亿美元",
        "growth_rate": "7.5%",
        "hot_products": ["手动工具", "锁具", "门窗五金", "水暖器材", "焊接器材"],
        "avg_price_range": "$0.5-30",
        "yiwu_advantage": "义乌二区五金专区，工具品类齐全，性价比高",
        "yiwu_index_score": 98.6,
        "target_markets": {
            "欧洲（义新欧班列直达）": {"share": "28%", "growth": "6.5%"},
            "中亚": {"share": "30%", "growth": "15.2%"},
            "中东": {"share": "22%", "growth": "12.8%"},
            "东南亚": {"share": "12%", "growth": "8.5%"},
            "非洲": {"share": "5%", "growth": "20.3%"},
            "南美": {"share": "3%", "growth": "10.7%"},
        },
    },
    "服装服饰": {
        "market_size": "1200亿美元",
        "growth_rate": "11.2%",
        "hot_products": ["女装", "童装", "运动服", "内衣", "休闲服饰"],
        "avg_price_range": "$2-35",
        "yiwu_advantage": "义乌四区服装专区，快时尚供应链优势明显",
        "yiwu_index_score": 104.2,
        "target_markets": {
            "欧洲（义新欧班列直达）": {"share": "32%", "growth": "10.5%"},
            "中亚": {"share": "22%", "growth": "18.3%"},
            "中东": {"share": "20%", "growth": "22.7%"},
            "东南亚": {"share": "16%", "growth": "9.8%"},
            "非洲": {"share": "6%", "growth": "26.5%"},
            "南美": {"share": "4%", "growth": "13.2%"},
        },
    },
    "家居装饰": {
        "market_size": "450亿美元",
        "growth_rate": "13.6%",
        "hot_products": ["墙贴壁纸", "窗帘", "地毯地垫", "装饰摆件", "灯饰"],
        "avg_price_range": "$1-40",
        "yiwu_advantage": "义乌五区家居装饰专区，新品更新速度快",
        "yiwu_index_score": 106.8,
        "target_markets": {
            "欧洲（义新欧班列直达）": {"share": "38%", "growth": "14.5%"},
            "中亚": {"share": "18%", "growth": "16.8%"},
            "中东": {"share": "22%", "growth": "20.3%"},
            "东南亚": {"share": "13%", "growth": "11.5%"},
            "非洲": {"share": "5%", "growth": "24.7%"},
            "南美": {"share": "4%", "growth": "15.3%"},
        },
    },
}
