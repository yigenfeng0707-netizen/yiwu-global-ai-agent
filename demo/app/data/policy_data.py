"""义乌小商品出海智能体 - 政策复制数据"""

# 39城市场采购贸易方式试点城市数据
CITY_1039_DATA = [
    {"city": "义乌", "province": "浙江", "approved_year": "2013", "main_categories": "日用百货、饰品配件、玩具、工艺品", "policy_benefits": "增值税免征、简化申报、通关便利化", "customs_code": "3313"},
    {"city": "海宁", "province": "浙江", "approved_year": "2016", "main_categories": "皮革制品、经编面料、袜子", "policy_benefits": "增值税免征、简化申报、跨境人民币结算", "customs_code": "3314"},
    {"city": "绍兴柯桥", "province": "浙江", "approved_year": "2016", "main_categories": "纺织面料、家纺产品、服装", "policy_benefits": "增值税免征、简化申报、组柜拼箱", "customs_code": "3315"},
    {"city": "湖州织里", "province": "浙江", "approved_year": "2016", "main_categories": "童装、棉布、床上用品", "policy_benefits": "增值税免征、简化申报、在线收结汇", "customs_code": "3316"},
    {"city": "台州路桥", "province": "浙江", "approved_year": "2016", "main_categories": "塑料制品、汽摩配件、缝制设备", "policy_benefits": "增值税免征、简化申报、信用担保", "customs_code": "3317"},
    {"city": "温州瓯海", "province": "浙江", "approved_year": "2016", "main_categories": "鞋类、眼镜、服装", "policy_benefits": "增值税免征、简化申报、出口信用保险", "customs_code": "3318"},
    {"city": "宁波江北", "province": "浙江", "approved_year": "2016", "main_categories": "小家电、文具、五金", "policy_benefits": "增值税免征、简化申报、港口直通", "customs_code": "3319"},
    {"city": "嘉兴平湖", "province": "浙江", "approved_year": "2016", "main_categories": "箱包、服装、童车", "policy_benefits": "增值税免征、简化申报、产地直采", "customs_code": "3320"},
    {"city": "杭州萧山", "province": "浙江", "approved_year": "2016", "main_categories": "羽绒制品、花边刺绣、伞具", "policy_benefits": "增值税免征、简化申报、数字贸易", "customs_code": "3321"},
    {"city": "金华永康", "province": "浙江", "approved_year": "2016", "main_categories": "五金工具、防盗门、保温杯", "policy_benefits": "增值税免征、简化申报、品牌出海", "customs_code": "3322"},
    {"city": "泉州", "province": "福建", "approved_year": "2016", "main_categories": "鞋服、石材、工艺品", "policy_benefits": "增值税免征、简化申报、对台贸易便利", "customs_code": "3505"},
    {"city": "厦门", "province": "福建", "approved_year": "2016", "main_categories": "电子产品、石材、茶叶", "policy_benefits": "增值税免征、简化申报、自贸区叠加优惠", "customs_code": "3502"},
    {"city": "广州", "province": "广东", "approved_year": "2016", "main_categories": "服装、皮具、电子产品", "policy_benefits": "增值税免征、简化申报、广交会资源", "customs_code": "4401"},
    {"city": "深圳", "province": "广东", "approved_year": "2016", "main_categories": "电子产品、智能硬件、珠宝", "policy_benefits": "增值税免征、简化申报、前海政策叠加", "customs_code": "4403"},
    {"city": "佛山", "province": "广东", "approved_year": "2016", "main_categories": "陶瓷、家具、家电", "policy_benefits": "增值税免征、简化申报、产业集群优势", "customs_code": "4406"},
    {"city": "东莞", "province": "广东", "approved_year": "2016", "main_categories": "电子元器件、玩具、家具", "policy_benefits": "增值税免征、简化申报、加工贸易转型", "customs_code": "4419"},
    {"city": "中山", "province": "广东", "approved_year": "2016", "main_categories": "灯饰、五金、家电", "policy_benefits": "增值税免征、简化申报、古镇灯都资源", "customs_code": "4420"},
    {"city": "汕头", "province": "广东", "approved_year": "2016", "main_categories": "玩具、内衣、工艺品", "policy_benefits": "增值税免征、简化申报、侨乡资源", "customs_code": "4405"},
    {"city": "成都", "province": "四川", "approved_year": "2016", "main_categories": "鞋类、家具、茶叶", "policy_benefits": "增值税免征、简化申报、中欧班列直达", "customs_code": "5101"},
    {"city": "重庆", "province": "重庆", "approved_year": "2016", "main_categories": "汽摩配件、电子产品、农产品", "policy_benefits": "增值税免征、简化申报、渝新欧班列直达", "customs_code": "5001"},
    {"city": "昆明", "province": "云南", "approved_year": "2016", "main_categories": "花卉、茶叶、珠宝", "policy_benefits": "增值税免征、简化申报、面向南亚东南亚", "customs_code": "5301"},
    {"city": "南宁", "province": "广西", "approved_year": "2016", "main_categories": "农产品、建材、轻工产品", "policy_benefits": "增值税免征、简化申报、面向东盟", "customs_code": "4501"},
    {"city": "长沙", "province": "湖南", "approved_year": "2016", "main_categories": "工程机械配件、烟花鞭炮、茶叶", "policy_benefits": "增值税免征、简化申报、湘欧快线", "customs_code": "4301"},
    {"city": "南昌", "province": "江西", "approved_year": "2016", "main_categories": "纺织品、陶瓷、农产品", "policy_benefits": "增值税免征、简化申报、赣欧班列", "customs_code": "3601"},
    {"city": "合肥", "province": "安徽", "approved_year": "2016", "main_categories": "家电、汽车配件、光伏产品", "policy_benefits": "增值税免征、简化申报、合新欧班列", "customs_code": "3401"},
    {"city": "郑州", "province": "河南", "approved_year": "2016", "main_categories": "服装、建材、农产品", "policy_benefits": "增值税免征、简化申报、郑欧班列", "customs_code": "4101"},
    {"city": "武汉", "province": "湖北", "approved_year": "2016", "main_categories": "光电子产品、汽车配件、纺织", "policy_benefits": "增值税免征、简化申报、汉欧班列", "customs_code": "4201"},
    {"city": "西安", "province": "陕西", "approved_year": "2016", "main_categories": "农产品、工艺品、机械设备", "policy_benefits": "增值税免征、简化申报、长安号班列", "customs_code": "6101"},
    {"city": "兰州", "province": "甘肃", "approved_year": "2016", "main_categories": "中药材、农产品、化工产品", "policy_benefits": "增值税免征、简化申报、面向中亚", "customs_code": "6201"},
    {"city": "乌鲁木齐", "province": "新疆", "approved_year": "2016", "main_categories": "纺织品、农产品、建材", "policy_benefits": "增值税免征、简化申报、面向中亚西亚", "customs_code": "6501"},
    {"city": "沈阳", "province": "辽宁", "approved_year": "2016", "main_categories": "机械设备、汽车配件、农产品", "policy_benefits": "增值税免征、简化申报、面向东北亚", "customs_code": "2101"},
    {"city": "大连", "province": "辽宁", "approved_year": "2016", "main_categories": "水产品、服装、石化产品", "policy_benefits": "增值税免征、简化申报、港口优势", "customs_code": "2102"},
    {"city": "哈尔滨", "province": "黑龙江", "approved_year": "2016", "main_categories": "农产品、木材、机电产品", "policy_benefits": "增值税免征、简化申报、面向俄罗斯", "customs_code": "2301"},
    {"city": "长春", "province": "吉林", "approved_year": "2016", "main_categories": "农产品、汽车配件、医药", "policy_benefits": "增值税免征、简化申报、面向东北亚", "customs_code": "2201"},
    {"city": "石家庄", "province": "河北", "approved_year": "2016", "main_categories": "纺织品、建材、医药", "policy_benefits": "增值税免征、简化申报、冀欧班列", "customs_code": "1301"},
    {"city": "唐山", "province": "河北", "approved_year": "2016", "main_categories": "陶瓷、钢材、建材", "policy_benefits": "增值税免征、简化申报、港口优势", "customs_code": "1302"},
    {"city": "济南", "province": "山东", "approved_year": "2016", "main_categories": "机械设备、纺织品、农产品", "policy_benefits": "增值税免征、简化申报、济欧班列", "customs_code": "3701"},
    {"city": "青岛", "province": "山东", "approved_year": "2016", "main_categories": "家电、纺织品、水产品", "policy_benefits": "增值税免征、简化申报、港口优势", "customs_code": "3702"},
    {"city": "临沂", "province": "山东", "approved_year": "2016", "main_categories": "板材、五金、劳保用品", "policy_benefits": "增值税免征、简化申报、商贸物流城", "customs_code": "3713"},
]

# 1039市场采购贸易政策详解
POLICY_1039_DETAIL = {
    "policy_name": "市场采购贸易方式（海关监管代码1039）",
    "policy_code": "1039",
    "background": "为解决小商品出口'多品种、多批次、小批量'的贸易特点，国务院于2013年在义乌率先试点市场采购贸易方式，后在39个城市推广复制",
    "key_points": [
        {
            "title": "增值税免征不退",
            "description": "市场采购贸易出口货物免征增值税，且不办理退税。经营者无需取得增值税专用发票即可出口，大幅降低合规成本",
            "benefit_level": "高",
        },
        {
            "title": "简化申报",
            "description": "实行'简化申报'制度，对商品编码实行'归并申报'，将多个小商品归并为一个大类申报，单票报关单商品项数由数十项缩减至5项以内",
            "benefit_level": "高",
        },
        {
            "title": "通关便利化",
            "description": "享受海关优先查验、快速放行等便利措施，出口通关时间压缩60%以上，实现'秒放'通关",
            "benefit_level": "高",
        },
        {
            "title": "跨境人民币结算",
            "description": "允许以人民币计价结算，规避汇率风险，简化外汇核销手续",
            "benefit_level": "中",
        },
        {
            "title": "组柜拼箱",
            "description": "允许多个商户的货物组柜拼箱出口，降低物流成本，适合小批量多品种的出口模式",
            "benefit_level": "中",
        },
        {
            "title": "在线收结汇",
            "description": "通过联网信息平台实现在线收结汇，资金到账速度快，结算效率高",
            "benefit_level": "中",
        },
    ],
    "applicable_conditions": [
        "在经认定的市场采购贸易试点区域内采购",
        "经由海关监管的采购地出口",
        "单票报关单商品货值15万美元（含）以下",
        "在市场采购贸易综合管理系统中备案",
        "出口商品不属于禁止出口商品",
    ],
    "operation_process": [
        {"step": 1, "title": "备案登记", "description": "在市场采购贸易综合管理系统中完成经营主体备案登记"},
        {"step": 2, "title": "商品采购", "description": "在试点市场内采购商品，取得供货商户信息"},
        {"step": 3, "title": "组货装箱", "description": "在指定监管场所完成组货装箱，生成装箱清单"},
        {"step": 4, "title": "简化申报", "description": "通过综合管理系统进行简化申报，归并商品编码"},
        {"step": 5, "title": "海关查验", "description": "海关实施便利化查验，优先放行"},
        {"step": 6, "title": "出口通关", "description": "货物出口，完成通关手续"},
        {"step": 7, "title": "收结汇", "description": "通过联网信息平台在线收结汇"},
    ],
    "tax_benefits": {
        "vat_exemption": True,
        "vat_description": "出口货物免征增值税，无需取得增值税专用发票",
        "income_tax": "按核定征收，应税所得率统一按5%核定",
        "stamp_duty": "免征",
        "compared_to_general_trade": {
            "general_trade_vat": "需取得增值税专用发票，退税率0%-13%",
            "market_purchase_vat": "直接免征，无需发票",
            "cost_saving": "每100万元出口额可节省合规成本约2-5万元",
        },
    },
}

# 义乌成功案例
YIWU_SUCCESS_CASES = [
    {
        "case_id": 1,
        "title": "义乌饰品出海中东——从个体户到千万出口商",
        "category": "饰品配件",
        "target_market": "中东（阿联酋、沙特）",
        "annual_export": "1200万美元",
        "key_strategies": [
            "利用1039模式简化申报，将200+SKU饰品归并为5大类出口",
            "通过义新欧班列+中东航线组合物流，运输成本降低30%",
            "利用免征增值税政策，无需取得进项发票，合规成本降低80%",
        ],
        "localization_tips": [
            "中东市场偏好金色、大尺寸饰品，需调整产品规格",
            "包装需符合清真认证要求",
            "建立当地仓储，实现48小时配送",
        ],
        "replication_difficulty": "中等",
        "replicable_points": [
            "1039简化申报模式可直接复制",
            "组柜拼箱降低物流成本的经验可复制",
            "免征增值税政策在39城均可享受",
        ],
    },
    {
        "case_id": 2,
        "title": "义乌玩具出口东南亚——RCEP+1039双政策红利",
        "category": "玩具",
        "target_market": "东南亚（印尼、泰国、越南）",
        "annual_export": "800万美元",
        "key_strategies": [
            "叠加RCEP关税优惠和1039增值税免征双重政策红利",
            "通过跨境人民币结算规避汇率风险",
            "利用在线收结汇平台，资金周转效率提升50%",
        ],
        "localization_tips": [
            "东南亚市场偏好益智类和户外类玩具",
            "需取得当地安全认证（如印尼SNI认证）",
            "建立本地化客服团队，提供多语言服务",
        ],
        "replication_difficulty": "较低",
        "replicable_points": [
            "RCEP+1039双政策叠加模式可在沿海城市复制",
            "跨境人民币结算在所有试点城市可用",
            "在线收结汇平台已全国联网",
        ],
    },
    {
        "case_id": 3,
        "title": "义乌日用百货出口欧洲——义新欧班列+1039模式",
        "category": "日用百货",
        "target_market": "欧洲（德国、法国、西班牙）",
        "annual_export": "2500万美元",
        "key_strategies": [
            "利用义新欧班列直达欧洲，比海运快2-3倍、比空运便宜60-80%",
            "1039模式通关便利化，出口通关时间压缩60%",
            "组柜拼箱模式，多商户共享集装箱，物流成本降低40%",
        ],
        "localization_tips": [
            "欧洲市场注重环保，需符合REACH法规",
            "产品包装需使用可回收材料",
            "建立欧洲海外仓，实现本地化配送",
        ],
        "replication_difficulty": "中等",
        "replicable_points": [
            "义新欧班列沿线城市均可复制此模式",
            "1039通关便利化在所有试点城市适用",
            "组柜拼箱模式可在商贸城集群城市推广",
        ],
    },
    {
        "case_id": 4,
        "title": "义乌针织品出口非洲——小批量多品种的1039典范",
        "category": "针织品",
        "target_market": "非洲（尼日利亚、肯尼亚、坦桑尼亚）",
        "annual_export": "600万美元",
        "key_strategies": [
            "利用1039单票15万美元以下简化申报，实现小批量高频次出口",
            "通过市场采购贸易综合管理系统在线备案，效率提升3倍",
            "免征增值税+核定征收所得税，综合税负降低70%",
        ],
        "localization_tips": [
            "非洲市场偏好鲜艳色彩和印花图案",
            "需适应热带气候，选择透气面料",
            "建立本地分销网络，利用集市渠道",
        ],
        "replication_difficulty": "较低",
        "replicable_points": [
            "小批量多品种出口模式适合所有试点城市",
            "在线备案系统全国统一，可直接使用",
            "免征增值税政策在39城完全一致",
        ],
    },
    {
        "case_id": 5,
        "title": "义乌电子电器出口中亚——EAEU+1039政策组合拳",
        "category": "电子电器",
        "target_market": "中亚（哈萨克斯坦、乌兹别克斯坦、吉尔吉斯斯坦）",
        "annual_export": "1500万美元",
        "key_strategies": [
            "叠加EAEU成员国间关税优惠和1039增值税免征",
            "利用义新欧班列中亚线路，运输时间缩短至8-12天",
            "通过跨境人民币结算，规避中亚货币贬值风险",
        ],
        "localization_tips": [
            "中亚市场偏好性价比高的中低端电子产品",
            "需取得EAEU认证（EAC标志）",
            "提供俄语说明书和包装标签",
        ],
        "replication_difficulty": "中等",
        "replicable_points": [
            "EAEU+1039政策组合可在西北试点城市复制",
            "义新欧班列中亚线路覆盖多个试点城市",
            "跨境人民币结算规避汇率风险的经验可复制",
        ],
    },
]

# 政策红利计算参数
POLICY_BENEFIT_PARAMS = {
    "vat_rate": 0.13,  # 增值税率13%
    "income_tax_rate": 0.05,  # 核定征收应税所得率5%
    "income_tax_bracket": 0.20,  # 小微企业税率20%
    "general_trade_compliance_cost_rate": 0.03,  # 一般贸易合规成本率3%
    "market_purchase_compliance_cost_rate": 0.005,  # 1039模式合规成本率0.5%
    "clearance_time_general": 3,  # 一般贸易通关时间(天)
    "clearance_time_1039": 1,  # 1039通关时间(天)
    "logistics_saving_rate": 0.30,  # 组柜拼箱物流节省率30%
    "max_value_per_shipment": 150000,  # 单票最高货值15万美元
}
