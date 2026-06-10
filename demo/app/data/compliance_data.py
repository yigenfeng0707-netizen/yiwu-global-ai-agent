"""义乌小商品出海智能体 - 合规数据模块"""

# 国家合规数据（扩展至欧洲、中亚、中东）
COUNTRY_COMPLIANCE = {
    # 欧洲
    "德国": {
        "certifications": ["CE认证", "RoHS认证", "REACH注册", "WEEE注册"],
        "import_duty_range": "3%-17%",
        "vat_rate": "19%",
        "special_requirements": "需提供德语标签和说明书，包装需符合VerpackG法规",
        "clearance_time": "3-5个工作日",
    },
    "法国": {
        "certifications": ["CE认证", "RoHS认证", "REACH注册", "EPR注册"],
        "import_duty_range": "3%-17%",
        "vat_rate": "20%",
        "special_requirements": "需提供法语标签，Triman标识，反浪费法合规",
        "clearance_time": "3-5个工作日",
    },
    "西班牙": {
        "certifications": ["CE认证", "RoHS认证", "REACH注册"],
        "import_duty_range": "3%-17%",
        "vat_rate": "21%",
        "special_requirements": "义新欧班列直达马德里，通关便利化",
        "clearance_time": "2-4个工作日",
    },
    "荷兰": {
        "certifications": ["CE认证", "RoHS认证", "REACH注册"],
        "import_duty_range": "3%-17%",
        "vat_rate": "21%",
        "special_requirements": "鹿特丹港为欧洲最大中转港，清关效率高",
        "clearance_time": "2-3个工作日",
    },
    "波兰": {
        "certifications": ["CE认证", "RoHS认证", "REACH注册"],
        "import_duty_range": "3%-17%",
        "vat_rate": "23%",
        "special_requirements": "马拉舍维奇为义新欧班列主要入境口岸",
        "clearance_time": "2-4个工作日",
    },
    # 中亚
    "哈萨克斯坦": {
        "certifications": ["EAC认证", "GOST-K认证"],
        "import_duty_range": "5%-15%",
        "vat_rate": "12%",
        "special_requirements": "需提供俄语/哈萨克语标签，义新欧班列7天直达阿拉木图",
        "clearance_time": "3-5个工作日",
    },
    "乌兹别克斯坦": {
        "certifications": ["UzDSt认证", "GOST-Uz认证"],
        "import_duty_range": "5%-20%",
        "vat_rate": "15%",
        "special_requirements": "需提供乌兹别克语/俄语标签",
        "clearance_time": "4-6个工作日",
    },
    "吉尔吉斯斯坦": {
        "certifications": ["EAC认证"],
        "import_duty_range": "5%-12%",
        "vat_rate": "12%",
        "special_requirements": "EAEU成员国，通关便利",
        "clearance_time": "2-4个工作日",
    },
    # 中东
    "沙特阿拉伯": {
        "certifications": ["SABER认证", "SASO认证", "Halal认证(食品)"],
        "import_duty_range": "5%-20%",
        "vat_rate": "15%",
        "special_requirements": "需通过SABER系统注册，产品需阿拉伯语标签",
        "clearance_time": "5-7个工作日",
    },
    "阿联酋": {
        "certifications": ["ECAS认证", "ESMA认证", "Halal认证(食品)"],
        "import_duty_range": "5%",
        "vat_rate": "5%",
        "special_requirements": "迪拜杰贝阿里自贸区可免税仓储，适合中转",
        "clearance_time": "3-5个工作日",
    },
    "伊朗": {
        "certifications": ["ISIRI认证", "COI检验"],
        "import_duty_range": "10%-55%",
        "vat_rate": "9%",
        "special_requirements": "义新欧班列14天直达德黑兰，需ISIRI标准符合性评估",
        "clearance_time": "5-8个工作日",
    },
    "土耳其": {
        "certifications": ["CE认证", "TSE认证"],
        "import_duty_range": "0%-30%",
        "vat_rate": "20%",
        "special_requirements": "需提供土耳其语标签，部分产品需TSE认证",
        "clearance_time": "3-5个工作日",
    },
    # 东南亚
    "印尼": {
        "certifications": ["SNI认证", "BPOM注册(食品/化妆品)", "POSTEL认证(电子)"],
        "import_duty_range": "0%-40%",
        "vat_rate": "11%",
        "special_requirements": "需印尼语标签，部分商品需进口配额",
        "clearance_time": "5-7个工作日",
    },
    "泰国": {
        "certifications": ["TISI认证", "FDA注册(食品/化妆品)"],
        "import_duty_range": "0%-80%",
        "vat_rate": "7%",
        "special_requirements": "需泰语标签，部分商品需进口许可证",
        "clearance_time": "3-5个工作日",
    },
    "越南": {
        "certifications": ["CR标志认证", "QC认证"],
        "import_duty_range": "0%-50%",
        "vat_rate": "10%",
        "special_requirements": "需越南语标签，RCEP优惠税率适用",
        "clearance_time": "3-5个工作日",
    },
    "马来西亚": {
        "certifications": ["SIRIM认证", "MCMC认证(电子)", "Halal认证(食品)"],
        "import_duty_range": "0%-60%",
        "vat_rate": "10%",
        "special_requirements": "需马来语/英语标签，Halal认证对穆斯林市场重要",
        "clearance_time": "3-5个工作日",
    },
    # 非洲
    "埃及": {
        "certifications": ["GOEIC注册", "COI检验"],
        "import_duty_range": "5%-40%",
        "vat_rate": "14%",
        "special_requirements": "需阿拉伯语标签，GOEIC进口商注册必须",
        "clearance_time": "5-8个工作日",
    },
    "尼日利亚": {
        "certifications": ["SONCAP认证", "NAFDAC注册(食品/药品)"],
        "import_duty_range": "5%-35%",
        "vat_rate": "7.5%",
        "special_requirements": "需SONCAP认证，清关流程较复杂",
        "clearance_time": "7-10个工作日",
    },
}

# 清关文件清单
CLEARANCE_DOCUMENTS = [
    {"name": "商业发票", "required": True, "description": "详细列明商品名称、数量、单价、总价"},
    {"name": "装箱单", "required": True, "description": "列明每箱商品明细、毛重、净重"},
    {"name": "提单/运单", "required": True, "description": "海运提单或义新欧班列铁路运单"},
    {"name": "原产地证", "required": True, "description": "中国原产地证书，RCEP优惠税率需FORM E"},
    {"name": "报关单", "required": True, "description": "1039市场采购贸易报关单或一般贸易报关单"},
    {"name": "合同", "required": False, "description": "买卖双方贸易合同"},
    {"name": "检验检疫证书", "required": False, "description": "特定品类（食品、动植物产品）需要"},
    {"name": "认证证书", "required": False, "description": "目标市场要求的CE/SABER/EAC等认证"},
    {"name": "1039备案单", "required": False, "description": "市场采购贸易方式出口需提供"},
    {"name": "保险单", "required": False, "description": "货物运输保险单据"},
]

# 义新欧班列关税优惠
YIXINOU_TARIFF_BENEFITS = {
    "description": "义新欧班列运输的货物可享受中欧班列通关便利化政策，部分商品通过中欧双边协定享受优惠税率",
    "benefits": [
        "铁路运输货物通关优先查验",
        "中欧班列沿线海关互认AEO企业",
        "1039市场采购贸易简化申报",
        "义乌保税物流中心(B型)提前退税",
        "中欧BIT协定下部分商品关税减免",
    ],
}

# RCEP优惠（东南亚方向）
RCEP_TARIFF_BENEFITS = {
    "description": "RCEP协定下中国出口至东盟国家的商品可享受优惠关税",
    "benefits": [
        "90%以上税目产品最终零关税",
        "原产地累积规则降低享惠门槛",
        "经核准出口商自主声明原产地",
        "快件和快递货物6小时放行",
    ],
}

# 品类特殊要求
CATEGORY_SPECIAL_REQUIREMENTS = {
    "日用百货": "食品接触材料需符合目标国食品安全标准（欧盟EC 1935/2004、美国FDA等）",
    "饰品配件": "需符合镍释放量标准（欧盟EN1811），铅镉含量限制（欧盟REACH附录17）",
    "玩具": "需符合目标国玩具安全标准（欧盟EN71、美国ASTM F963、中东SASO等），必须有CE/ASTM标识",
    "文具办公用品": "学生用品需符合安全标准（欧盟EN71-1/2/3、美国LHAMA），墨水需无毒认证",
    "针织品": "需符合纺织品标签法规（欧盟EU 1007/2011），部分需Oeko-Tex认证",
    "工艺品": "仿真花/装饰品需符合阻燃标准，含电池产品需电池指令合规",
    "电子电器": "需CE认证（欧盟）、EAC认证（EAEU）、SABER认证（沙特），EMC和LVD指令合规",
    "五金工具": "手动工具需符合EN标准，锁具需安全等级认证，水暖器材需WRAS/ACS认证",
    "服装服饰": "需符合纺织品标签法规，儿童服装需EN14682安全标准，羽绒产品需IDFB认证",
    "家居装饰": "灯饰需CE/UL认证，地毯需阻燃测试，墙纸需VOC释放量检测",
}

# 认证流程
CERTIFICATION_PROCESS = {
    "CE认证": {
        "steps": ["确定适用指令", "进行风险评估", "编制技术文件", "进行产品测试", "签署符合性声明", "加贴CE标志"],
        "estimated_time": "4-8周",
        "estimated_cost": "¥5,000-50,000",
    },
    "SABER认证": {
        "steps": ["注册SABER账户", "选择产品HS编码", "提交测试报告", "获取PC证书", "申请SC证书"],
        "estimated_time": "2-4周",
        "estimated_cost": "¥3,000-20,000",
    },
    "EAC认证": {
        "steps": ["确定CU TR技术法规", "选择认证方案", "样品测试", "工厂审核(1C方案)", "签发EAC证书"],
        "estimated_time": "3-6周",
        "estimated_cost": "¥8,000-80,000",
    },
    "SNI认证": {
        "steps": ["提交申请", "样品测试", "工厂审核", "签发SNI证书"],
        "estimated_time": "4-8周",
        "estimated_cost": "¥10,000-60,000",
    },
}

# 通关时效
CUSTOMS_TIMELINE = {
    "义新欧班列": {
        "义乌出发": "0天",
        "阿拉山口/霍尔果斯出境": "2-3天",
        "哈萨克斯坦清关": "5-7天",
        "波兰马拉舍维奇": "10-12天",
        "德国杜伊斯堡": "14-16天",
        "西班牙马德里": "18-21天",
    },
    "海运": {
        "义乌-宁波港": "1天(陆运)",
        "宁波-欧洲基本港": "28-35天",
        "宁波-中东迪拜": "18-22天",
        "宁波-东南亚": "7-14天",
    },
}
