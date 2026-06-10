"""义乌小商品出海智能体 - 数据源模块"""

import random
from typing import Dict, List, Any


class DataSourceBase:
    """数据源基类"""

    name: str = "base"
    description: str = ""

    def fetch(self, category: str, region: str = "") -> Dict[str, Any]:
        raise NotImplementedError


class YiwuMarketDataSource(DataSourceBase):
    """义乌小商品城数据源"""

    name = "义乌小商品城"
    description = "义乌国际商贸城7.5万商户、210万+SKU实时数据"

    # 品类对应的热门产品
    CATEGORY_PRODUCTS = {
        "日用百货": [
            {"name": "厨房收纳架", "price_range": "$2-8", "moq": 200, "shops": 580},
            {"name": "不锈钢清洁球", "price_range": "$0.1-0.3", "moq": 5000, "shops": 320},
            {"name": "硅胶厨具套装", "price_range": "$3-12", "moq": 100, "shops": 450},
            {"name": "一次性PE手套", "price_range": "$0.5-2/盒", "moq": 500, "shops": 280},
            {"name": "卫浴置物架", "price_range": "$5-15", "moq": 100, "shops": 360},
        ],
        "饰品配件": [
            {"name": "合金项链套装", "price_range": "$0.5-3", "moq": 300, "shops": 890},
            {"name": "亚克力发夹", "price_range": "$0.1-0.5", "moq": 1000, "shops": 520},
            {"name": "树脂纽扣", "price_range": "$0.02-0.1", "moq": 5000, "shops": 340},
            {"name": "涤纶丝带", "price_range": "$0.3-1.5/卷", "moq": 200, "shops": 280},
            {"name": "亚克力珠串", "price_range": "$0.2-1", "moq": 500, "shops": 410},
        ],
        "玩具": [
            {"name": "益智积木", "price_range": "$3-15", "moq": 100, "shops": 620},
            {"name": "毛绒熊", "price_range": "$2-8", "moq": 200, "shops": 480},
            {"name": "遥控车", "price_range": "$5-20", "moq": 50, "shops": 350},
            {"name": "水枪", "price_range": "$1-5", "moq": 300, "shops": 290},
            {"name": "DIY手工套装", "price_range": "$2-10", "moq": 150, "shops": 380},
        ],
        "文具办公用品": [
            {"name": "中性笔套装", "price_range": "$0.3-2", "moq": 500, "shops": 560},
            {"name": "A5笔记本", "price_range": "$0.5-3", "moq": 200, "shops": 420},
            {"name": "桌面收纳盒", "price_range": "$1-5", "moq": 100, "shops": 310},
            {"name": "水彩笔套装", "price_range": "$1-6", "moq": 200, "shops": 280},
            {"name": "学生文具套装", "price_range": "$2-8", "moq": 100, "shops": 450},
        ],
        "针织品": [
            {"name": "纯棉运动袜", "price_range": "$0.3-1/双", "moq": 1000, "shops": 780},
            {"name": "羊绒围巾", "price_range": "$3-12", "moq": 100, "shops": 320},
            {"name": "针织毛线帽", "price_range": "$1-4", "moq": 200, "shops": 450},
            {"name": "触屏手套", "price_range": "$0.5-2", "moq": 300, "shops": 380},
            {"name": "手工毛线", "price_range": "$1-5/团", "moq": 100, "shops": 260},
        ],
        "工艺品": [
            {"name": "装饰油画", "price_range": "$3-20", "moq": 50, "shops": 520},
            {"name": "仿真花束", "price_range": "$1-8", "moq": 100, "shops": 680},
            {"name": "圣诞装饰球", "price_range": "$0.2-1", "moq": 1000, "shops": 890},
            {"name": "水晶相框", "price_range": "$2-10", "moq": 100, "shops": 340},
            {"name": "树脂摆件", "price_range": "$1-6", "moq": 200, "shops": 410},
        ],
        "电子电器": [
            {"name": "USB小风扇", "price_range": "$1-5", "moq": 200, "shops": 560},
            {"name": "LED灯带", "price_range": "$2-10/米", "moq": 100, "shops": 620},
            {"name": "手机壳", "price_range": "$0.3-2", "moq": 500, "shops": 890},
            {"name": "电子闹钟", "price_range": "$2-8", "moq": 100, "shops": 340},
            {"name": "电源适配器", "price_range": "$1-5", "moq": 200, "shops": 420},
        ],
        "五金工具": [
            {"name": "多功能扳手套装", "price_range": "$3-15", "moq": 100, "shops": 450},
            {"name": "密码锁", "price_range": "$2-8", "moq": 200, "shops": 380},
            {"name": "门把手", "price_range": "$1-5", "moq": 300, "shops": 320},
            {"name": "水龙头", "price_range": "$3-12", "moq": 100, "shops": 290},
            {"name": "电烙铁套装", "price_range": "$5-20", "moq": 50, "shops": 210},
        ],
        "服装服饰": [
            {"name": "女装T恤", "price_range": "$2-8", "moq": 100, "shops": 780},
            {"name": "童装套装", "price_range": "$3-12", "moq": 100, "shops": 560},
            {"name": "运动套装", "price_range": "$5-18", "moq": 50, "shops": 420},
            {"name": "内衣套装", "price_range": "$1-5", "moq": 200, "shops": 380},
            {"name": "休闲卫衣", "price_range": "$4-15", "moq": 80, "shops": 490},
        ],
        "家居装饰": [
            {"name": "PVC墙贴", "price_range": "$0.5-3", "moq": 200, "shops": 560},
            {"name": "遮光窗帘", "price_range": "$5-20", "moq": 50, "shops": 420},
            {"name": "客厅地毯", "price_range": "$8-30", "moq": 30, "shops": 350},
            {"name": "北欧风摆件", "price_range": "$2-10", "moq": 100, "shops": 480},
            {"name": "创意台灯", "price_range": "$5-20", "moq": 50, "shops": 380},
        ],
    }

    def fetch(self, category: str, region: str = "") -> Dict[str, Any]:
        products = self.CATEGORY_PRODUCTS.get(category, [])
        return {
            "source": self.name,
            "category": category,
            "products": products,
            "total_shops": 75000,
            "total_skus": 2100000,
            "market_index": round(random.uniform(98, 110), 1),
        }


class YixinouLogisticsDataSource(DataSourceBase):
    """义新欧班列物流数据源"""

    name = "义新欧班列"
    description = "义新欧班列19条线路、50国160城物流数据"

    ROUTES = [
        {"name": "义乌-马德里", "days": 21, "frequency": "每周3班", "cost_20ft": "$3200", "cost_40ft": "$4800"},
        {"name": "义乌-伦敦", "days": 18, "frequency": "每周2班", "cost_20ft": "$3500", "cost_40ft": "$5200"},
        {"name": "义乌-德黑兰", "days": 14, "frequency": "每周2班", "cost_20ft": "$2800", "cost_40ft": "$4200"},
        {"name": "义乌-阿拉木图", "days": 7, "frequency": "每周4班", "cost_20ft": "$1800", "cost_40ft": "$2800"},
        {"name": "义乌-莫斯科", "days": 10, "frequency": "每周3班", "cost_20ft": "$2400", "cost_40ft": "$3600"},
        {"name": "义乌-明斯克", "days": 12, "frequency": "每周2班", "cost_20ft": "$2600", "cost_40ft": "$3900"},
        {"name": "义乌-杜伊斯堡", "days": 16, "frequency": "每周3班", "cost_20ft": "$3000", "cost_40ft": "$4500"},
        {"name": "义乌-布拉格", "days": 15, "frequency": "每周2班", "cost_20ft": "$2900", "cost_40ft": "$4400"},
    ]

    def fetch(self, category: str = "", region: str = "") -> Dict[str, Any]:
        routes = self.ROUTES
        if region:
            routes = [r for r in routes if region in r["name"]]
        return {
            "source": self.name,
            "total_routes": 19,
            "countries_covered": 50,
            "cities_connected": 160,
            "annual_trips": 1600,
            "routes": routes,
            "advantages": [
                "比海运快2-3倍",
                "比空运便宜60-80%",
                "通关便利化，优先查验",
                "1039市场采购贸易简化申报",
                "义乌始发，直接装箱发运",
            ],
        }


class AmazonDataSource(DataSourceBase):
    """Amazon平台数据源"""

    name = "Amazon"
    description = "Amazon全球平台销售数据"

    def fetch(self, category: str, region: str = "") -> Dict[str, Any]:
        base_prices = {
            "日用百货": (5, 25), "饰品配件": (3, 15), "玩具": (8, 35),
            "文具办公用品": (3, 18), "针织品": (4, 20), "工艺品": (5, 30),
            "电子电器": (10, 50), "五金工具": (8, 40), "服装服饰": (8, 35),
            "家居装饰": (10, 45),
        }
        price_range = base_prices.get(category, (5, 30))
        return {
            "source": self.name,
            "category": category,
            "avg_selling_price": f"${price_range[0]}-{price_range[1]}",
            "competition_level": random.choice(["高", "中", "中高"]),
            "monthly_search_volume": f"{random.randint(10, 500)}K",
            "top_sellers": random.randint(50, 300),
            "review_avg": round(random.uniform(3.8, 4.5), 1),
        }


class AlibabaDataSource(DataSourceBase):
    """Alibaba.com数据源"""

    name = "Alibaba.com"
    description = "Alibaba.com国际站B2B数据"

    def fetch(self, category: str, region: str = "") -> Dict[str, Any]:
        return {
            "source": self.name,
            "category": category,
            "supplier_count": random.randint(500, 5000),
            "avg_moq": f"{random.randint(50, 500)}件",
            "price_range": f"${random.randint(1, 10)}-${random.randint(15, 50)}",
            "inquiry_trend": random.choice(["上升", "稳定", "快速上升"]),
        }


class IndustryReportDataSource(DataSourceBase):
    """行业报告数据源"""

    name = "行业报告"
    description = "义乌指数及行业研究报告"

    REPORTS = {
        "日用百货": {"market_size": "580亿美元", "growth": "12.5%", "trend": "稳步增长"},
        "饰品配件": {"market_size": "320亿美元", "growth": "15.8%", "trend": "快速增长"},
        "玩具": {"market_size": "950亿美元", "growth": "8.6%", "trend": "稳定增长"},
        "文具办公用品": {"market_size": "280亿美元", "growth": "6.8%", "trend": "平稳"},
        "针织品": {"market_size": "420亿美元", "growth": "10.2%", "trend": "稳步增长"},
        "工艺品": {"market_size": "260亿美元", "growth": "9.5%", "trend": "季节性波动"},
        "电子电器": {"market_size": "780亿美元", "growth": "14.3%", "trend": "快速增长"},
        "五金工具": {"market_size": "350亿美元", "growth": "7.5%", "trend": "稳定增长"},
        "服装服饰": {"market_size": "1200亿美元", "growth": "11.2%", "trend": "快速增长"},
        "家居装饰": {"market_size": "450亿美元", "growth": "13.6%", "trend": "快速增长"},
    }

    def fetch(self, category: str, region: str = "") -> Dict[str, Any]:
        report = self.REPORTS.get(category, {})
        return {
            "source": self.name,
            "category": category,
            **report,
            "yiwu_index": round(random.uniform(98, 110), 1),
        }


class DataSourceManager:
    """数据源管理器"""

    def __init__(self):
        self.sources: Dict[str, DataSourceBase] = {}
        self._register_default_sources()

    def _register_default_sources(self):
        self.register(YiwuMarketDataSource())
        self.register(YixinouLogisticsDataSource())
        self.register(AmazonDataSource())
        self.register(AlibabaDataSource())
        self.register(IndustryReportDataSource())

    def register(self, source: DataSourceBase):
        self.sources[source.name] = source

    def get(self, name: str) -> DataSourceBase | None:
        return self.sources.get(name)

    def fetch_all(self, category: str, region: str = "") -> List[Dict[str, Any]]:
        results = []
        for source in self.sources.values():
            try:
                data = source.fetch(category, region)
                results.append(data)
            except Exception:
                continue
        return results

    def fetch_by_source(self, source_name: str, category: str, region: str = "") -> Dict[str, Any] | None:
        source = self.get(source_name)
        if source:
            return source.fetch(category, region)
        return None

    def list_sources(self) -> List[Dict[str, str]]:
        return [{"name": s.name, "description": s.description} for s in self.sources.values()]
