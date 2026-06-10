"""义乌小商品出海智能体 - 内容数据模块"""

SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "英语"},
    {"code": "de", "name": "德语"},
    {"code": "fr", "name": "法语"},
    {"code": "es", "name": "西班牙语"},
    {"code": "ar", "name": "阿拉伯语"},
    {"code": "ru", "name": "俄语"},
    {"code": "kk", "name": "哈萨克语"},
    {"code": "ja", "name": "日语"},
]

SUPPORTED_PLATFORMS = [
    {"code": "amazon", "name": "Amazon"},
    {"code": "alibaba", "name": "Alibaba.com"},
    {"code": "tiktok", "name": "TikTok Shop"},
    {"code": "temu", "name": "Temu"},
]

# SEO关键词（按品类×语言）
SEO_KEYWORDS = {
    "日用百货": {
        "en": ["daily necessities", "household items", "kitchen supplies", "cleaning tools", "bathroom accessories"],
        "de": ["Haushaltswaren", "Küchenbedarf", "Reinigungsgeräte", "Badezimmerzubehör", "Alltagsgegenstände"],
        "fr": ["articles ménagers", "fournitures de cuisine", "outils de nettoyage", "accessoires salle de bain"],
        "es": ["artículos diarios", "suministros de cocina", "herramientas de limpieza", "accesorios de baño"],
        "ar": ["مستلزمات يومية", "لوازم مطبخ", "أدوات تنظيف", "إكسسوارات حمام"],
        "ru": ["товары повседневного спроса", "кухонные принадлежности", "средства для уборки"],
        "kk": ["күнделікті тауарлар", "ас үй жабдықтары", "тазарту құралдары"],
        "ja": ["日用品", "キッチン用品", "掃除用具", "バスアクセサリー"],
    },
    "饰品配件": {
        "en": ["fashion jewelry", "hair accessories", "buttons zippers", "ribbon lace", "bead accessories"],
        "de": ["Modeschmuck", "Haarzubehör", "Knöpfe Reißverschlüsse", "Bänder Spitzen"],
        "fr": ["bijoux de mode", "accessoires cheveux", "boutons fermetures", "rubans dentelles"],
        "es": ["joyería de moda", "accesorios para el cabello", "botones cremalleras", "cintas encajes"],
        "ar": ["مجوهرات أزياء", "إكسسوارات شعر", "أزرار سحابات", "شرائط دانتيل"],
        "ru": ["модные украшения", "аксессуары для волос", "пуговицы молнии", "ленты кружева"],
        "kk": ["сәнді зергерлік бұйымдар", "шаш аксессуарлары", "түймелер"],
        "ja": ["ファッションジュエリー", "ヘアアクセサリー", "ボタンファスナー", "リボンレース"],
    },
    "玩具": {
        "en": ["educational toys", "plush toys", "RC toys", "water guns", "DIY crafts"],
        "de": ["Lernspielzeug", "Plüschtiere", "Ferngesteuertes Spielzeug", "Wasserpistolen", "Bastelsets"],
        "fr": ["jouets éducatifs", "peluches", "jouets télécommandés", "pistolets à eau", "bricolage"],
        "es": ["juguetes educativos", "peluches", "juguetes RC", "pistolas de agua", "manualidades"],
        "ar": ["ألعاب تعليمية", "دمى محشوة", "ألعاب تحكم عن بعد", "مسدسات ماء", "أشغال يدوية"],
        "ru": ["обучающие игрушки", "плюшевые игрушки", "радиоуправляемые игрушки", "водные пистолеты"],
        "kk": ["оқытушы ойыншықтар", "құшақтайтын ойыншықтар", "радиобасқарылатын ойыншықтар"],
        "ja": ["知育玩具", "ぬいぐるみ", "ラジコン玩具", "水鉄砲", "DIY工作"],
    },
    "文具办公用品": {
        "en": ["pens", "notebooks", "office organizers", "art supplies", "school stationery"],
        "de": ["Kugelschreiber", "Notizbücher", "Büroorganizer", "Kunstbedarf", "Schulbedarf"],
        "fr": ["stylos", "cahiers", "organiseurs bureau", "fournitures artistiques", "fournitures scolaires"],
        "es": ["bolígrafos", "cuadernos", "organizadores oficina", "suministros arte", "material escolar"],
        "ar": ["أقلام", "دفاتر", "منظمات مكتبية", "لوازم فنية", "قرطاسية مدرسية"],
        "ru": ["ручки", "тетради", "органайзеры для офиса", "художественные принадлежности"],
        "kk": ["қаламдар", "дәптерлер", "кеңсе ұйымдастырғыштары", "өнер құралдары"],
        "ja": ["ペン", "ノート", "オフィス整理", "画材", "文房具"],
    },
    "针织品": {
        "en": ["socks", "scarves", "hats", "gloves", "yarn"],
        "de": ["Socken", "Schals", "Hüte", "Handschuhe", "Garn"],
        "fr": ["chaussettes", "écharpes", "chapeaux", "gants", "fil à tricoter"],
        "es": ["calcetines", "bufandas", "sombreros", "guantes", "hilo"],
        "ar": ["جوارب", "أوشحة", "قبعات", "قفازات", "خيوط"],
        "ru": ["носки", "шарфы", "шапки", "перчатки", "пряжа"],
        "kk": ["шұлықтар", "жамылғылар", "бас киімдер", "қолғаптар", "жіптер"],
        "ja": ["靴下", "マフラー", "帽子", "手袋", "毛糸"],
    },
    "工艺品": {
        "en": ["decorative paintings", "artificial flowers", "festival supplies", "photo frames", "crystal crafts"],
        "de": ["Dekorative Gemälde", "Kunstblumen", "Festbedarf", "Bilderrahmen", "Kristallkunst"],
        "fr": ["peintures décoratives", "fleurs artificielles", "articles de fête", "cadres photo", "cristaux"],
        "es": ["pinturas decorativas", "flores artificiales", "artículos festivos", "marcos de fotos", "artesanía de cristal"],
        "ar": ["لوحات زخرفية", "زهور اصطناعية", "لوازم مهرجانات", "إطارات صور", "حرف الكريستال"],
        "ru": ["декоративные картины", "искусственные цветы", "праздничные товары", "фоторамки", "хрустальные изделия"],
        "kk": ["декоративті суреттер", "жасанды гүлдер", "мереке тауарлары", "фоторамкалар"],
        "ja": ["装飾画", "造花", "フェスティバル用品", "フォトフレーム", "クリスタル工芸"],
    },
    "电子电器": {
        "en": ["small appliances", "LED lights", "phone accessories", "electronic clocks", "power adapters"],
        "de": ["Kleingeräte", "LED-Leuchten", "Handyzubehör", "Elektronische Uhren", "Netzteile"],
        "fr": ["petits électroménagers", "éclairage LED", "accessoires téléphone", "horloges électroniques", "adaptateurs"],
        "es": ["electrodomésticos pequeños", "luces LED", "accesorios teléfono", "relojes electrónicos", "adaptadores"],
        "ar": ["أجهزة صغيرة", "إضاءة LED", "إكسسوارات هاتف", "ساعات إلكترونية", "محولات طاقة"],
        "ru": ["мелкая бытовая техника", "LED-освещение", "аксессуары для телефонов", "электронные часы", "адаптеры питания"],
        "kk": ["шағын аспаптар", "LED шамдар", "телефон аксессуарлары", "электронды сағаттар"],
        "ja": ["小型家電", "LED照明", "スマホアクセサリー", "電子時計", "電源アダプター"],
    },
    "五金工具": {
        "en": ["hand tools", "locks", "door window hardware", "plumbing supplies", "welding equipment"],
        "de": ["Handwerkzeuge", "Schlösser", "Tür- und Fenstereisenwaren", "Sanitärbedarf", "Schweißgeräte"],
        "fr": ["outils à main", "serrures", "quincaillerie portes fenêtres", "fournitures plomberie", "équipement soudure"],
        "es": ["herramientas manuales", "cerraduras", "ferretería puertas ventanas", "suministros plomería", "equipo soldadura"],
        "ar": ["أدوات يدوية", "أقفال", "معدات أبواب نوافذ", "لوازم سباكة", "معدات لحام"],
        "ru": ["ручные инструменты", "замки", "дверная фурнитура", "сантехника", "сварочное оборудование"],
        "kk": ["қол құралдар", "құлыптар", "есік терезе жабдықтары", "сантехника тауарлары"],
        "ja": ["手工具", "錠前", "建物金物", "水道用品", "溶接機器"],
    },
    "服装服饰": {
        "en": ["women clothing", "kids clothing", "sportswear", "underwear", "casual wear"],
        "de": ["Damenkleidung", "Kinderkleidung", "Sportkleidung", "Unterwäsche", "Freizeitkleidung"],
        "fr": ["vêtements femme", "vêtements enfant", "sportswear", "linge", "vêtements décontractés"],
        "es": ["ropa mujer", "ropa niños", "ropa deportiva", "ropa interior", "ropa casual"],
        "ar": ["ملابس نسائية", "ملابس أطفال", "ملابس رياضية", "ملابس داخلية", "ملابس غير رسمية"],
        "ru": ["женская одежда", "детская одежда", "спортивная одежда", "нижнее белье", "повседневная одежда"],
        "kk": ["әйел киімі", "балалар киімі", "спорт киімі", "ішкі киім", "күнделікті киім"],
        "ja": ["レディース服", "キッズ服", "スポーツウェア", "下着", "カジュアルウェア"],
    },
    "家居装饰": {
        "en": ["wall stickers", "curtains", "rugs mats", "decorative ornaments", "lighting"],
        "de": ["Wandaufkleber", "Vorhänge", "Teppiche Matten", "Deko-Ornamente", "Beleuchtung"],
        "fr": ["autocollants muraux", "rideaux", "tapis paillassons", "ornements décoratifs", "éclairage"],
        "es": ["pegatinas pared", "cortinas", "alfombras", "ornamentos decorativos", "iluminación"],
        "ar": ["ملصقات جدارية", "ستائر", "سجاد بسط", "زخارف ديكور", "إضاءة"],
        "ru": ["настенные наклейки", "шторы", "коврики", "декоративные украшения", "освещение"],
        "kk": ["қабырға стикерлері", "перделер", "кілемшелер", "декорациялар", "жарықтандыру"],
        "ja": ["ウォールステッカー", "カーテン", "ラグマット", "装飾オーナメント", "照明"],
    },
}

# 卖点模板
HIGHLIGHT_TEMPLATES = {
    "日用百货": [
        {"icon": "🏠", "text": "义乌直供，价格优势明显"},
        {"icon": "✅", "text": "品质保障，符合国际标准"},
        {"icon": "📦", "text": "小批量起订，灵活采购"},
        {"icon": "🚂", "text": "义新欧班列直达，物流便捷"},
    ],
    "饰品配件": [
        {"icon": "💎", "text": "义乌饰品城直供，款式最新"},
        {"icon": "🎨", "text": "设计多样，紧跟国际潮流"},
        {"icon": "💰", "text": "源头价格，利润空间大"},
        {"icon": "🌍", "text": "全球最大饰品集散中心"},
    ],
    "玩具": [
        {"icon": "🧸", "text": "义乌玩具城直供，品类齐全"},
        {"icon": "🔒", "text": "符合EN71/ASTM安全标准"},
        {"icon": "🎯", "text": "益智+娱乐，市场需求旺盛"},
        {"icon": "🎄", "text": "圣诞季热销，提前备货"},
    ],
    "文具办公用品": [
        {"icon": "✏️", "text": "义乌文具专区直供"},
        {"icon": "📚", "text": "学生+办公，双市场覆盖"},
        {"icon": "🏷️", "text": "价格极具竞争力"},
        {"icon": "📦", "text": "小批量起订，试单无忧"},
    ],
    "针织品": [
        {"icon": "🧦", "text": "全球最大袜子生产基地"},
        {"icon": "❄️", "text": "季节性强，冬季需求旺盛"},
        {"icon": "🎨", "text": "花色丰富，定制灵活"},
        {"icon": "💰", "text": "规模化生产，成本优势"},
    ],
    "工艺品": [
        {"icon": "🎨", "text": "圣诞用品占全球出口80%"},
        {"icon": "🌸", "text": "仿真花工艺精湛"},
        {"icon": "🎁", "text": "节日+日常，全年需求"},
        {"icon": "🚂", "text": "义新欧班列直达欧洲"},
    ],
    "电子电器": [
        {"icon": "💡", "text": "LED灯饰品类齐全"},
        {"icon": "🔌", "text": "CE/EAC/SABER认证支持"},
        {"icon": "📱", "text": "手机配件全球热销"},
        {"icon": "🏠", "text": "小家电出海蓝海"},
    ],
    "五金工具": [
        {"icon": "🔧", "text": "手动工具性价比高"},
        {"icon": "🔐", "text": "锁具品类齐全"},
        {"icon": "🏗️", "text": "基建需求带动增长"},
        {"icon": "🌍", "text": "中亚市场潜力巨大"},
    ],
    "服装服饰": [
        {"icon": "👗", "text": "快时尚供应链优势"},
        {"icon": "🏃", "text": "运动休闲趋势强劲"},
        {"icon": "👶", "text": "童装市场增长快"},
        {"icon": "🏷️", "text": "小批量快反，灵活供应"},
    ],
    "家居装饰": [
        {"icon": "🏠", "text": "家居装饰趋势向好"},
        {"icon": "💡", "text": "灯饰品类丰富"},
        {"icon": "🖼️", "text": "墙贴壁纸热销"},
        {"icon": "🚂", "text": "义新欧班列直达欧洲"},
    ],
}

# 社媒文案模板
SOCIAL_COPY_TEMPLATES = {
    "日用百货": {
        "hook": "还在为日常用品价格发愁？",
        "pain_point": "当地超市价格高、选择少",
        "solution": "来自义乌的优质日用品，价格低至1折起",
        "cta": "点击链接，限时优惠！",
        "hashtags": ["#义乌好货", "#日用百货", "#跨境优选", "#义新欧直达"],
    },
    "饰品配件": {
        "hook": "想要最新款时尚饰品？",
        "pain_point": "当地款式老旧、价格昂贵",
        "solution": "义乌饰品城直供，全球最新款式",
        "cta": "立即选购，做最in的自己！",
        "hashtags": ["#义乌饰品", "#时尚首饰", "#跨境好货", "#源头直供"],
    },
    "玩具": {
        "hook": "给孩子最好的礼物！",
        "pain_point": "安全认证的益智玩具难找",
        "solution": "义乌玩具城直供，EN71/ASTM认证保障",
        "cta": "限时折扣，快来看看！",
        "hashtags": ["#义乌玩具", "#益智玩具", "#安全认证", "#儿童礼物"],
    },
    "文具办公用品": {
        "hook": "办公学习必备好物！",
        "pain_point": "文具选择少、价格高",
        "solution": "义乌文具专区直供，品类丰富价格优",
        "cta": "批量采购更优惠！",
        "hashtags": ["#义乌文具", "#办公用品", "#学生必备", "#批量采购"],
    },
    "针织品": {
        "hook": "保暖又时尚的针织好物！",
        "pain_point": "当地针织品款式单一",
        "solution": "义乌针织品直供，花色丰富品质好",
        "cta": "冬季热卖中，快来抢购！",
        "hashtags": ["#义乌针织", "#保暖好物", "#时尚穿搭", "#冬季必备"],
    },
    "工艺品": {
        "hook": "装点生活的艺术好物！",
        "pain_point": "节日装饰品价格高、选择少",
        "solution": "义乌工艺品直供，全球80%圣诞用品来自义乌",
        "cta": "节日季提前备货！",
        "hashtags": ["#义乌工艺", "#圣诞用品", "#家居装饰", "#节日必备"],
    },
    "电子电器": {
        "hook": "智能生活从好物开始！",
        "pain_point": "小家电价格高、选择有限",
        "solution": "义乌电子电器直供，认证齐全品质保障",
        "cta": "科技好物，限时特惠！",
        "hashtags": ["#义乌电子", "#智能家居", "#LED灯饰", "#跨境好货"],
    },
    "五金工具": {
        "hook": "专业工具，品质之选！",
        "pain_point": "当地工具价格高、品质参差",
        "solution": "义乌五金直供，性价比之王",
        "cta": "专业级工具，点击选购！",
        "hashtags": ["#义乌五金", "#专业工具", "#DIY必备", "#品质保障"],
    },
    "服装服饰": {
        "hook": "快时尚，穿出你的风格！",
        "pain_point": "当地服装款式老旧、价格高",
        "solution": "义乌服装直供，快时尚供应链优势",
        "cta": "新品上架，限时优惠！",
        "hashtags": ["#义乌服装", "#快时尚", "#跨境服饰", "#潮流穿搭"],
    },
    "家居装饰": {
        "hook": "让家更温馨的装饰好物！",
        "pain_point": "家居装饰品选择少、价格高",
        "solution": "义乌家居装饰直供，品种丰富价格优",
        "cta": "一键装扮你的家！",
        "hashtags": ["#义乌家居", "#家居装饰", "#灯饰", "#义新欧直达"],
    },
}

# 描述模板
DESCRIPTION_TEMPLATES = {
    "日用百货": "精选义乌优质日用百货，涵盖厨房用品、清洁工具、收纳整理等品类。义乌国际商贸城直供，价格优势明显，品质可靠。支持1039市场采购贸易，义新欧班列直达欧洲，物流便捷高效。",
    "饰品配件": "义乌饰品城直供时尚饰品配件，涵盖首饰、发饰、纽扣拉链等品类。全球最大饰品集散中心，款式最新、价格最优。支持小批量起订，灵活采购。",
    "玩具": "义乌玩具城直供各类玩具，涵盖益智玩具、毛绒玩具、遥控玩具等。符合EN71/ASTM国际安全标准，品质保障。圣诞季热销品类，义新欧班列直达欧洲。",
    "文具办公用品": "义乌文具专区直供，涵盖笔类、本册、办公收纳等品类。价格极具竞争力，支持小批量起订。学生+办公双市场覆盖，全年需求稳定。",
    "针织品": "全球最大袜子生产基地直供，涵盖袜子、围巾、帽子等品类。规模化生产成本优势明显，花色丰富定制灵活。冬季需求旺盛，提前备货。",
    "工艺品": "义乌工艺品直供，圣诞用品占全球出口80%。涵盖装饰画、仿真花、节日用品等品类。义新欧班列直达欧洲，节日季物流保障。",
    "电子电器": "义乌电子电器直供，涵盖小家电、LED灯饰、手机配件等品类。CE/EAC/SABER认证支持，品质保障。小家电出海蓝海市场，增长潜力大。",
    "五金工具": "义乌五金专区直供，涵盖手动工具、锁具、门窗五金等品类。性价比高，中亚市场潜力巨大。基建需求带动增长，长期需求稳定。",
    "服装服饰": "义乌服装专区直供，快时尚供应链优势明显。涵盖女装、童装、运动服等品类。小批量快反灵活供应，紧跟国际潮流。",
    "家居装饰": "义乌家居装饰直供，涵盖墙贴壁纸、窗帘、灯饰等品类。义新欧班列直达欧洲，家居装饰趋势向好。品种丰富价格优，一键装扮温馨家。",
}

# 标题模板
TITLE_TEMPLATES = {
    "日用百货": "义乌直供日用百货 | 厨房清洁收纳 | 义新欧班列直达 | 1039市场采购",
    "饰品配件": "义乌饰品城直供 | 时尚首饰发饰 | 全球最新款式 | 小批量起订",
    "玩具": "义乌玩具城直供 | 益智毛绒遥控 | EN71/ASTM认证 | 圣诞季热销",
    "文具办公用品": "义乌文具直供 | 笔类本册收纳 | 学生办公必备 | 价格优势",
    "针织品": "义乌针织直供 | 袜子围巾帽子 | 全球最大生产基地 | 冬季热卖",
    "工艺品": "义乌工艺品直供 | 圣诞装饰仿真花 | 全球80%份额 | 义新欧直达",
    "电子电器": "义乌电子直供 | 小家电LED灯饰 | CE/EAC认证 | 智能生活",
    "五金工具": "义乌五金直供 | 手动工具锁具 | 性价比之王 | 中亚热销",
    "服装服饰": "义乌服装直供 | 快时尚供应链 | 女装童装运动 | 小批量快反",
    "家居装饰": "义乌家居直供 | 墙贴灯饰窗帘 | 义新欧直达 | 温馨之选",
}

# 广告文案模板
AD_COPY_TEMPLATES = {
    "日用百货": {
        "headline": "义乌好货 全球直达",
        "body": "来自世界小商品之都的优质日用品，义新欧班列14天直达欧洲，1039市场采购贸易更便捷",
        "cta_button": "立即采购",
    },
    "饰品配件": {
        "headline": "全球饰品 看义乌",
        "body": "世界最大饰品集散中心直供，最新款式最优价格，小批量起订灵活采购",
        "cta_button": "浏览新款",
    },
    "玩具": {
        "headline": "安全玩具 义乌智造",
        "body": "EN71/ASTM国际安全认证，益智+娱乐双重价值，圣诞季提前备货享优惠",
        "cta_button": "查看详情",
    },
    "文具办公用品": {
        "headline": "文具好物 义乌直供",
        "body": "品类丰富价格优，学生办公全覆盖，批量采购更优惠",
        "cta_button": "批量订购",
    },
    "针织品": {
        "headline": "温暖针织 义乌制造",
        "body": "全球最大袜子生产基地，花色丰富品质好，冬季热卖中",
        "cta_button": "选购保暖",
    },
    "工艺品": {
        "headline": "节日装饰 义乌首选",
        "body": "全球80%圣诞用品来自义乌，义新欧班列直达欧洲，节日季无忧备货",
        "cta_button": "节日备货",
    },
    "电子电器": {
        "headline": "智能好物 义乌精选",
        "body": "小家电LED灯饰手机配件，CE/EAC/SABER认证齐全，品质保障",
        "cta_button": "科技好物",
    },
    "五金工具": {
        "headline": "专业五金 义乌直供",
        "body": "手动工具锁具水暖器材，性价比之王，中亚市场热销中",
        "cta_button": "专业选购",
    },
    "服装服饰": {
        "headline": "快时尚 义乌速度",
        "body": "快时尚供应链优势，小批量快反灵活供应，紧跟国际潮流",
        "cta_button": "时尚选购",
    },
    "家居装饰": {
        "headline": "温馨家居 义乌装扮",
        "body": "墙贴灯饰窗帘地毯，义新欧班列直达欧洲，品种丰富价格优",
        "cta_button": "装扮家居",
    },
}
