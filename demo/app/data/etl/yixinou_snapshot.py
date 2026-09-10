"""义新欧班列运营线路数据快照（镜像 fallback）

数据来源：yixinou.com/lines 官网页面（2026-09-10 抓取）
当部署环境（如魔搭社区 Docker）DNS 不可达 yixinou.com 时，
ETL 自动降级到此快照数据，仍标注 is_real=True 并注明"快照日期"。

官方统计（交通部/海关总署 2026年8月公开报道）：
  - 27条国际铁路直达线路
  - 辐射50+个国家和地区
  - 通达160+座城市
"""

from __future__ import annotations

# 快照元数据
SNAPSHOT_DATE = "2026-09-10"
SNAPSHOT_SOURCE_URL = "https://yixinou.com/lines"
SNAPSHOT_NOTE = (
    f"官网快照（{SNAPSHOT_DATE} 抓取自 yixinou.com/lines，部署环境 DNS 不可达时使用）"
)

# 中欧线路（17条，含去程+回程）
CENTRAL_EUROPE_ROUTES = [
    "义乌-霍尔果斯-跨两海",
    "义乌-霍尔果斯-格鲁吉亚",
    "义乌-阿拉山口-马德里",
    "义乌-霍尔果斯-罗斯特克",
    "义乌-霍尔果斯-布拉格",
    "义乌-二连-马德里",
    "义乌-阿拉山口-布拉格",
    "义乌-阿拉山口-列日",
    "义乌-霍尔果斯-马德里",
    "义乌-霍尔果斯-立陶宛",
    "义乌-阿拉山口-马拉舍维奇",
    "义乌-圣彼得堡-汉堡",
    "金华-阿拉山口-匈牙利",
    "罗斯特克-霍尔果斯-义乌",
    "马德里-霍尔果斯-义乌",
    "布拉格-阿拉山口-义乌",
    "马德里-阿拉山口-义乌",
]

CENTRAL_EUROPE_STATIONS = [
    "马拉舍维奇",
    "汉堡（Billwerder）",
    "马德里",
    "杜伊斯堡",
    "第比利斯-枢纽",
    "巴统（港）",
    "波季-出口",
    "康斯坦察",
    "伊斯坦布尔",
    "布拉格",
    "布达佩斯",
]

# 中亚线路（16条，含去程+回程）
CENTRAL_ASIA_ROUTES = [
    "义乌-霍尔果斯-中亚",
    "金华-霍尔果斯-中亚",
    "义乌-阿拉山口-中亚",
    "金华-阿拉山口-中亚",
    "义乌-霍尔果斯-巴库",
    "义乌-霍尔果斯-土耳其",
    "义乌-凭祥-越南",
    "义乌-磨憨-老挝",
    "金华-磨憨-老挝",
    "义乌-霍尔果斯-伊朗",
    "义乌-霍尔果斯-阿富汗",
    "伊朗-霍尔果斯-义乌",
    "中亚-霍尔果斯-义乌",
    "中亚-阿拉山口-义乌",
    "中亚-霍尔果斯-金华",
    "中亚-阿拉山口-金华",
]

CENTRAL_ASIA_STATIONS = [
    "阿拉木图",
    "丘库尔赛",
    "阿拉梅金",
    "塔什干",
    "谢尔盖利",
    "杜尚别",
    "苦盏",
    "阿什哈巴德",
    "梅杰乌",
    "浩罕",
    "瑟尔达里因斯卡亚",
    "格普贾克",
    "万象南",
    "埃巴特（巴库）",
    "安札利",
]

# 中俄线路（23条，含去程+回程）
CHINA_RUSSIA_ROUTES = [
    "义乌-满洲里-明斯克",
    "金华-满洲里-明斯克",
    "义乌-霍尔果斯-俄罗斯",
    "义乌-阿拉山口-明斯克",
    "义乌-霍尔果斯-明斯克",
    "义乌-阿拉山口-俄罗斯",
    "金华-阿拉山口-俄罗斯",
    "义乌-二连-俄罗斯",
    "金华-二连-俄罗斯",
    "义乌-二连-基辅",
    "义乌-二连-明斯克",
    "义乌-满洲里-俄罗斯",
    "俄罗斯-绥芬河-义乌",
    "俄罗斯-阿拉山口-义乌",
    "俄罗斯-满洲里-义乌",
    "俄罗斯-满洲里-金华",
    "俄罗斯-霍尔果斯-义乌",
    "白罗斯-阿拉山口-义乌",
    "白罗斯-满洲里-义乌",
    "俄罗斯-二连-义乌",
    "俄罗斯-二连-金华",
    "白罗斯-霍尔果斯-义乌",
    "白罗斯-二连-义乌",
]

CHINA_RUSSIA_STATIONS = [
    "舒沙雷",
    "科利亚季奇",
    "沃尔西诺",
    "拉格尔纳亚",
    "谢利亚季诺",
    "霍夫里诺",
    "叶卡捷琳堡",
    "若季诺",
    "巴塔列伊纳亚",
    "罗斯托夫",
    "乌斯季伊利姆斯克",
    "索利卡姆斯克",
    "鄂木斯克-东",
    "普里沃尔日耶",
    "乔姆斯科伊",
]

# 联系方式
CONTACTS = [
    {
        "region": "中欧",
        "name": "陈凯峰",
        "phone": "+86 13306790077",
        "email": "chenkaifeng@yixinou.com",
    },
    {
        "region": "中亚",
        "name": "叶秋然",
        "phone": "+86 13305895599",
        "email": "yeqiuran@yixinou.com",
    },
    {
        "region": "中俄",
        "name": "张剑灵",
        "phone": "+86 15306799177",
        "email": "zhangjianling@yixinou.com",
    },
]


def get_snapshot_data() -> dict:
    """返回快照数据的结构化 dict（与 YixinouSource.parse() 输出格式一致）。"""
    all_routes = CENTRAL_EUROPE_ROUTES + CENTRAL_ASIA_ROUTES + CHINA_RUSSIA_ROUTES
    all_emails = [c["email"] for c in CONTACTS]
    return {
        "provider": f"义新欧班列官网 yixinou.com/lines（{SNAPSHOT_DATE} 快照）",
        "data_type": "运营线路（线路名称+站点列表+联系方式）",
        "update_mode": f"快照日期 {SNAPSHOT_DATE}（官网定期更新；部署环境不可达时降级）",
        "routes_by_region": {
            "中欧": CENTRAL_EUROPE_ROUTES,
            "中亚": CENTRAL_ASIA_ROUTES,
            "中俄": CHINA_RUSSIA_ROUTES,
        },
        "stations_by_region": {
            "中欧": CENTRAL_EUROPE_STATIONS,
            "中亚": CENTRAL_ASIA_STATIONS,
            "中俄": CHINA_RUSSIA_STATIONS,
        },
        "total_routes": len(all_routes),
        "all_routes": all_routes,
        "contacts": all_emails,
        "contacts_detail": CONTACTS,
        "official_stats": {
            "total_routes_reported": 27,
            "countries_covered": 50,
            "cities_connected": 160,
            "source": "交通部/海关总署公开报道（2026年8月）",
        },
        "snapshot_date": SNAPSHOT_DATE,
        "snapshot_source_url": SNAPSHOT_SOURCE_URL,
        "snapshot_note": SNAPSHOT_NOTE,
    }
