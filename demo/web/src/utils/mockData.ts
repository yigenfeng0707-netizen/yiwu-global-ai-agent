/**
 * Mock 数据 - 当后端 API 不可用时自动使用
 * 数据结构与 api.ts 中定义的接口完全一致
 */

// ==================== 市场洞察 Mock ====================
export const mockMarketInsight = (category: string, region: string) => ({
  category,
  region,
  market_size: '580亿美元',
  market_growth: '12.5%',
  hot_categories: [
    { name: '厨房用品', share: '28', growth: '15.2%' },
    { name: '清洁工具', share: '22', growth: '12.8%' },
    { name: '收纳整理', share: '18', growth: '18.5%' },
    { name: '一次性用品', share: '15', growth: '10.3%' },
    { name: '卫浴用品', share: '12', growth: '22.1%' },
  ],
  trends: [
    { description: '欧洲消费者对环保日用品需求持续增长，可降解材料产品增速达35%', impact: 'high' },
    { description: '义新欧班列运输成本较空运低60-80%，时效较海运快2-3倍', impact: 'high' },
    { description: '1039市场采购贸易政策红利持续释放，通关时间压缩60%', impact: 'medium' },
    { description: 'RCEP协定下东南亚市场关税优惠，90%以上税目最终零关税', impact: 'medium' },
    { description: '跨境电商平台(Amazon/Temu/TikTok Shop)推动小批量多品种出口', impact: 'low' },
  ],
  price_tiers: [
    { tier: '低端', price_range: '$0.5-3', volume_share: '45' },
    { tier: '中端', price_range: '$3-10', volume_share: '35' },
    { tier: '高端', price_range: '$10-50', volume_share: '20' },
  ],
  competitors: [
    { name: '义乌商户集群', market_share: '35%', strength: '品类齐全、价格优势、供应链完善' },
    { name: '广东制造商', market_share: '25%', strength: '规模化生产、品牌化运营' },
    { name: '东南亚本地供应商', market_share: '20%', strength: '地缘优势、低关税' },
    { name: '印度制造商', market_share: '12%', strength: '成本优势' },
    { name: '土耳其供应商', market_share: '8%', strength: '欧洲地缘优势' },
  ],
  recommendations: [
    { product: '厨房收纳架', rating: 92, reason: '欧洲家居收纳需求旺盛，利润空间大', predicted_sales: '5万件/月' },
    { product: '环保清洁套装', rating: 88, reason: '环保趋势推动，溢价能力强', predicted_sales: '3万件/月' },
    { product: '一次性餐饮用品', rating: 85, reason: '餐饮行业刚需，复购率高', predicted_sales: '8万件/月' },
    { product: '卫浴收纳套装', rating: 82, reason: '家居升级需求，组合销售利润高', predicted_sales: '2万件/月' },
  ],
  risks: [
    { description: '欧盟REACH法规更新，部分化学品含量限制加严', level: 'high', mitigation: '提前做好产品检测，选择合规供应商' },
    { description: '海运运费波动风险', level: 'medium', mitigation: '优先选择义新欧班列，运费更稳定' },
    { description: '目标市场竞争加剧', level: 'low', mitigation: '差异化产品定位，强化品牌建设' },
  ],
  yiwu_index: { current: 102.8, change: 1.35, trend: '上涨', category_score: 105.2 },
  data_sources: ['义乌指数', '海关总署', 'Eurostat', '世界银行'],
});

// ==================== 智能选品 Mock ====================
export const mockSmartSelection = (category: string, budget: string, region: string) => ({
  category,
  budget,
  region,
  overall_score: { total: 85, level: '优秀' },
  market_opportunity: {
    market_size: '580亿美元',
    growth_rate: '12.5%',
    competition_level: '中等',
    entry_difficulty: '较低',
  },
  product_recommendations: [
    {
      product: '厨房收纳架',
      scores: { '综合评分': 92, '市场需求': 90, '利润空间': 88, '竞争程度': 85, '供应链稳定性': 95 },
      suggested_moq: 500,
      estimated_roi: '35%',
    },
    {
      product: '环保清洁套装',
      scores: { '综合评分': 88, '市场需求': 85, '利润空间': 92, '竞争程度': 80, '供应链稳定性': 90 },
      suggested_moq: 300,
      estimated_roi: '42%',
    },
    {
      product: '一次性餐饮用品',
      scores: { '综合评分': 85, '市场需求': 92, '利润空间': 75, '竞争程度': 78, '供应链稳定性': 88 },
      suggested_moq: 1000,
      estimated_roi: '28%',
    },
  ],
  profit_analysis: {
    cost_breakdown: { '采购成本': '¥8.5/件', '物流成本': '¥2.3/件', '认证成本': '¥0.5/件', '包装成本': '¥0.8/件', '平台佣金': '¥1.5/件' },
    revenue: { '建议售价': '$5.99/件', '预计月销量': '5000件', '月收入预估': '$29,950' },
    break_even: { '盈亏平衡销量': '1800件', '盈亏平衡周期': '12天' },
  },
  supply_recommendations: [
    { supplier: '义乌三区·永辉日用品', location: '义乌三区', moq: '500件', price_range: '¥6-9/件', rating: 4.8, recommended: true },
    { supplier: '义乌三区·佳洁清洁用品', location: '义乌三区', moq: '300件', price_range: '¥7-11/件', rating: 4.6, recommended: true },
    { supplier: '义乌一区·鑫达收纳', location: '义乌一区', moq: '800件', price_range: '¥5-8/件', rating: 4.3, recommended: false },
  ],
  action_plan: {
    phase1: { name: '市场验证', tasks: ['选择2-3款核心产品', '小批量试单(100-200件)', '收集市场反馈数据', '评估销售表现'] },
    phase2: { name: '规模扩展', tasks: ['加大畅销品采购量', '优化物流方案(义新欧班列)', '拓展销售渠道', '建立品牌形象'] },
    phase3: { name: '深度运营', tasks: ['开发差异化产品', '建立海外仓', '本地化营销推广', '构建长期供应链合作'] },
  },
});

// ==================== 供应链 Mock ====================
export const mockSupplyChain = (category: string, region: string, budget: string) => ({
  category,
  region,
  budget,
  suppliers: [
    { supplier: '义乌三区·永辉日用品', product: '厨房收纳架', district: '三区', moq: 500, unit_price: '¥8.5', delivery_days: 7, rating: 4.8, certifications: ['ISO9001', 'CE'], recommended: true },
    { supplier: '义乌三区·佳洁清洁', product: '环保清洁套装', district: '三区', moq: 300, unit_price: '¥10.2', delivery_days: 5, rating: 4.6, certifications: ['ISO9001', 'CE', 'FSC'], recommended: true },
    { supplier: '义乌一区·鑫达收纳', product: '收纳整理盒', district: '一区', moq: 800, unit_price: '¥6.8', delivery_days: 10, rating: 4.3, certifications: ['ISO9001'], recommended: false },
    { supplier: '义乌三区·恒达日用', product: '一次性餐具', district: '三区', moq: 2000, unit_price: '¥0.35', delivery_days: 5, rating: 4.5, certifications: ['FDA', 'CE'], recommended: true },
  ],
  purchase_info: {
    avg_price_range: '¥5-15/件',
    yiwu_advantage: '义乌三区日用品专区直供，品类齐全，价格优势明显，支持小批量混批',
    yiwu_index_score: 105.2,
    price_trend: '稳中有降',
    sample_available: true,
    sample_lead_time: '3-5天',
    bulk_lead_time: '7-15天',
    payment_terms: ['30%预付', '70%出货前付清', '月结(信用客户)'],
  },
  logistics: {
    source: '义新欧班列',
    total_routes: 19,
    countries_covered: 50,
    cities_connected: 160,
    routes: [
      { name: '义乌-马德里', days: 21, frequency: '每周3班', cost_20ft: '$2,800', cost_40ft: '$4,200' },
      { name: '义乌-伦敦', days: 18, frequency: '每周2班', cost_20ft: '$3,200', cost_40ft: '$4,800' },
      { name: '义乌-杜伊斯堡', days: 14, frequency: '每周3班', cost_20ft: '$2,800', cost_40ft: '$4,200' },
      { name: '义乌-阿拉木图', days: 7, frequency: '每周4班', cost_20ft: '$1,800', cost_40ft: '$2,800' },
      { name: '义乌-德黑兰', days: 14, frequency: '每周2班', cost_20ft: '$2,200', cost_40ft: '$3,500' },
    ],
    advantages: ['比海运快2-3倍', '比空运便宜60-80%', '通关便利化', '固定班期稳定可靠'],
  },
  trade_1039: {
    applicable: true,
    name: '市场采购贸易方式（1039）',
    description: '在经认定的市场集聚区采购商品，单票报关单商品货值15万（含）以下，可直接办理出口通关',
    advantages: ['免征增值税，不办理出口退税', '简化报关流程，实行简化申报', '允许多主体收汇，支持人民币结算', '通关便利化，查验率低', '适合小商品多品种出口'],
    conditions: ['在义乌市场集聚区内采购', '单票货值15万美元以下', '在指定口岸出口'],
    max_value_per_shipment: '$150,000',
    simplified_declaration: true,
    vat_exemption: true,
  },
  supply_score: { total: 88, level: '优秀', dimensions: { '供应商质量': 90, '价格竞争力': 85, '交期稳定性': 88, '物流便利性': 92, '政策支持': 95 } },
  yiwu_trade_city: { total_shops: 75000, total_skus: 2100000, district: '三区' },
});

// ==================== 物流 Mock ====================
export const mockLogistics = () => ({
  source: '义新欧班列',
  total_routes: 19,
  countries_covered: 50,
  cities_connected: 160,
  routes: [
    { name: '义乌-马德里', days: 21, frequency: '每周3班', cost_20ft: '$2,800', cost_40ft: '$4,200' },
    { name: '义乌-伦敦', days: 18, frequency: '每周2班', cost_20ft: '$3,200', cost_40ft: '$4,800' },
    { name: '义乌-杜伊斯堡', days: 14, frequency: '每周3班', cost_20ft: '$2,800', cost_40ft: '$4,200' },
    { name: '义乌-阿拉木图', days: 7, frequency: '每周4班', cost_20ft: '$1,800', cost_40ft: '$2,800' },
    { name: '义乌-莫斯科', days: 10, frequency: '每周3班', cost_20ft: '$2,200', cost_40ft: '$3,500' },
    { name: '义乌-明斯克', days: 12, frequency: '每周2班', cost_20ft: '$2,000', cost_40ft: '$3,200' },
    { name: '义乌-德黑兰', days: 14, frequency: '每周2班', cost_20ft: '$2,200', cost_40ft: '$3,500' },
  ],
  advantages: ['比海运快2-3倍', '比空运便宜60-80%', '通关便利化', '固定班期稳定可靠', '全程温控可选'],
});

// ==================== 内容生成 Mock ====================
export const mockContentGeneration = (product_name: string, category: string, platform: string, target_language: string) => ({
  product_name,
  category,
  platform,
  target_language,
  content: {
    title: `${product_name} | 义乌直供 | 品质保障 | 义新欧班列直达`,
    description: `精选义乌优质${product_name}，源自义乌国际商贸城直供。品质可靠，价格优势明显，支持1039市场采购贸易。义新欧班列14天直达欧洲，物流便捷高效。小批量起订，灵活采购，适合跨境电商卖家。`,
    highlights: [
      { icon: '🏠', text: '义乌直供，价格优势明显' },
      { icon: '✅', text: '品质保障，符合国际标准' },
      { icon: '📦', text: '小批量起订，灵活采购' },
      { icon: '🚂', text: '义新欧班列直达，物流便捷' },
    ],
    seo_keywords: [product_name, '义乌直供', '跨境优选', '义新欧直达', '1039市场采购', '品质保障'],
  },
  marketing: {
    social_copy: {
      hook: '还在为采购价格发愁？',
      pain_point: '当地价格高、选择少',
      solution: `来自义乌的优质${product_name}，价格低至1折起`,
      cta: '点击链接，限时优惠！',
      hashtags: ['#义乌好货', `#${product_name}`, '#跨境优选', '#义新欧直达'],
    },
    ad_copy: {
      headline: '义乌好货 全球直达',
      body: `来自世界小商品之都的优质${product_name}，义新欧班列14天直达欧洲，1039市场采购贸易更便捷`,
      cta_button: '立即采购',
    },
  },
  platform_compliance: {
    warnings: ['请确保产品图片符合平台规范', '建议添加多语言产品描述', '注意目标市场认证要求'],
  },
});

// ==================== 合规查询 Mock ====================
export const mockCompliance = (category: string, target_country: string) => ({
  category,
  target_country,
  certifications: [
    { name: 'CE认证', required: true, estimated_time: '4-8周', estimated_cost: '¥5,000-50,000' },
    { name: 'RoHS认证', required: true, estimated_time: '2-4周', estimated_cost: '¥3,000-15,000' },
    { name: 'REACH注册', required: true, estimated_time: '2-6周', estimated_cost: '¥2,000-20,000' },
    { name: 'WEEE注册', required: false, estimated_time: '4-8周', estimated_cost: '¥8,000-30,000' },
  ],
  clearance_documents: [
    { name: '商业发票', required: true, description: '详细列明商品名称、数量、单价、总价' },
    { name: '装箱单', required: true, description: '列明每箱商品明细、毛重、净重' },
    { name: '提单/运单', required: true, description: '海运提单或义新欧班列铁路运单' },
    { name: '原产地证', required: true, description: '中国原产地证书，RCEP优惠税率需FORM E' },
    { name: '报关单', required: true, description: '1039市场采购贸易报关单或一般贸易报关单' },
    { name: '认证证书', required: false, description: '目标市场要求的CE/RoHS等认证' },
  ],
  compliance_check: {
    checks: [
      { item: 'CE标志合规', status: 'pass', risk_level: 'low' },
      { item: 'RoHS有害物质限制', status: 'pass', risk_level: 'low' },
      { item: 'REACH化学品注册', status: 'pass', risk_level: 'medium' },
      { item: '产品标签(目标国语言)', status: 'fail', risk_level: 'high' },
      { item: '包装合规(VerpackG)', status: 'pass', risk_level: 'low' },
    ],
    overall_status: 'conditional_pass',
  },
  special_requirements: '需提供德语标签和说明书，包装需符合VerpackG法规',
  tariff_benefits: {
    description: '义新欧班列运输的货物可享受中欧班列通关便利化政策',
    benefits: ['铁路运输货物通关优先查验', '中欧班列沿线海关互认AEO企业', '1039市场采购贸易简化申报', '义乌保税物流中心(B型)提前退税'],
  },
});

// ==================== 关税计算 Mock ====================
export const mockTariff = (product_value: number) => ({
  product_value,
  tariff_rate: '8%',
  tariff_amount: Math.round(product_value * 0.08),
  vat_rate: '19%',
  vat_amount: Math.round(product_value * 0.19),
  import_tax: Math.round(product_value * 0.03),
  total_tax: Math.round(product_value * 0.08 + product_value * 0.19 + product_value * 0.03),
  total_cost: Math.round(product_value * 1.3),
  rcep_benefits: null,
});

// ==================== 客服 Mock ====================
export const mockChatResponse = (message: string, category: string) => ({
  reply: { text: `您好！关于您提到的"${message}"，义乌国际商贸城拥有7.5万商户、210万+SKU，是全球最大的小商品批发市场。${category}品类在义乌有丰富的供应商资源，支持小批量起订。建议您通过1039市场采购贸易方式出口，可享受增值税免征、简化申报等政策红利。如需了解更多详情，欢迎继续咨询！` },
  emotion: { type: 'positive', label: '积极', color: '#00C9A7' },
  dispute: { detected: false },
  needs_human_escalation: false,
  session_id: `session_${Date.now()}`,
});

export const mockChatReply = (message: string) => ({
  reply: {
    text: `关于"${message}"的问题，根据义乌小商品出海经验：\n\n1. 1039市场采购贸易模式可免征增值税\n2. 义新欧班列14-21天直达欧洲\n3. 建议通过义乌国际商贸城7.5万商户进行采购\n\n如需更详细的信息，请告诉我具体的品类和目标市场。`,
  },
  emotion: { type: 'neutral', label: '中性', color: '#9ca3af' },
  dispute: { detected: false },
  needs_human_escalation: false,
  session_id: 'mock_session',
});

export const mockFAQ = (category: string, language: string) => ({
  faqs: [
    { q_zh: '什么是1039市场采购贸易？', a_zh: '1039市场采购贸易是在经认定的市场集聚区采购商品，单票报关单货值15万美元以下，可简化申报、免征增值税。义乌是全国首批试点城市。', q_en: 'What is 1039 market purchase trade?', a_en: 'Market purchase trade allows simplified declaration and VAT exemption for goods under $150,000 purchased in designated market clusters. Yiwu is a pilot city.' },
    { q_zh: `${category}的MOQ是多少？`, a_zh: `义乌${category}MOQ灵活，一般1-5箱起订，支持混批。1039模式下单票货值15万美元以下可简化申报。`, q_en: `What is the MOQ for ${category}?`, a_en: `Flexible MOQ from 1-5 cartons, mixed batches supported. Under 1039 mode, simplified declaration for shipments under $150,000.` },
    { q_zh: '义新欧班列有哪些路线？', a_zh: '义新欧班列已开通19条线路，覆盖50多个国家160多个城市。主要路线包括义乌-马德里、义乌-伦敦、义乌-德黑兰、义乌-阿拉木图等。', q_en: 'What routes does Yixinou Railway have?', a_en: '19 routes covering 50+ countries and 160+ cities. Main routes: Yiwu-Madrid, Yiwu-London, Yiwu-Tehran, Yiwu-Almaty.' },
    { q_zh: '如何开始义乌小商品跨境出口？', a_zh: '步骤：1)在义乌市场选品采购 2)办理1039市场采购贸易备案 3)选择物流方式(义新欧班列/海运) 4)办理出口报关 5)目标市场清关配送。', q_en: 'How to start Yiwu cross-border export?', a_en: 'Steps: 1) Source in Yiwu market 2) Register for 1039 trade 3) Choose logistics 4) Export customs 5) Destination clearance.' },
  ],
  category,
});

// ==================== 全链路工作流 Mock ====================
export const mockPipeline = () => ({
  state: {
    market_insight: {
      category: '日用百货', region: '欧洲',
      market_size: '580亿美元', market_growth: '12.5%',
      trends: [
        { description: '欧洲消费者对环保日用品需求持续增长，可降解材料产品增速达35%', impact: 'high' },
        { description: '义新欧班列运输成本较空运低60-80%，时效较海运快2-3倍', impact: 'high' },
        { description: '1039市场采购贸易政策红利持续释放，通关时间压缩60%', impact: 'medium' },
        { description: 'RCEP协定下东南亚市场关税优惠，90%以上税目最终零关税', impact: 'medium' },
      ],
      competitors: [
        { name: '义乌商户集群', market_share: '35%', strength: '品类齐全、价格优势、供应链完善' },
        { name: '广东制造商', market_share: '25%', strength: '规模化生产、品牌化运营' },
        { name: '东南亚本地供应商', market_share: '20%', strength: '地缘优势、低关税' },
      ],
      recommendations: [
        { product: '厨房收纳架', rating: 92, reason: '欧洲家居收纳需求旺盛，利润空间大' },
        { product: '环保清洁套装', rating: 88, reason: '环保趋势推动，溢价能力强' },
        { product: '一次性餐饮用品', rating: 85, reason: '餐饮行业刚需，复购率高' },
      ],
      yiwu_index: { current: 102.8, change: 1.35, trend: '上涨' },
    },
    smart_selection: {
      category: '日用百货', budget: '中', region: '欧洲',
      overall_score: { total: 85, level: '优秀' },
      market_opportunity: { market_size: '580亿美元', growth_rate: '12.5%', competition_level: '中等', entry_difficulty: '较低' },
      product_recommendations: [
        { product: '厨房收纳架', scores: { '综合评分': 92, '市场需求': 90, '利润空间': 88, '竞争程度': 85, '供应链稳定性': 95 }, suggested_moq: 500, estimated_roi: '35%' },
        { product: '环保清洁套装', scores: { '综合评分': 88, '市场需求': 85, '利润空间': 92, '竞争程度': 80, '供应链稳定性': 90 }, suggested_moq: 300, estimated_roi: '42%' },
        { product: '一次性餐饮用品', scores: { '综合评分': 85, '市场需求': 92, '利润空间': 75, '竞争程度': 78, '供应链稳定性': 88 }, suggested_moq: 1000, estimated_roi: '28%' },
      ],
    },
    supply_chain: {
      category: '日用百货', region: '欧洲', budget: '中',
      supply_score: { total: 88, level: '优秀', dimensions: { '供应商质量': 90, '价格竞争力': 85, '交期稳定性': 88, '物流便利性': 92, '政策支持': 95 } },
      suppliers: [
        { supplier: '义乌三区·永辉日用品', product: '厨房收纳架', district: '三区', moq: 500, unit_price: '¥8.5', delivery_days: 7, rating: 4.8, certifications: ['ISO9001', 'CE'], recommended: true },
        { supplier: '义乌三区·佳洁清洁', product: '环保清洁套装', district: '三区', moq: 300, unit_price: '¥10.2', delivery_days: 5, rating: 4.6, certifications: ['ISO9001', 'CE', 'FSC'], recommended: true },
        { supplier: '义乌一区·鑫达收纳', product: '收纳整理盒', district: '一区', moq: 800, unit_price: '¥6.8', delivery_days: 10, rating: 4.3, certifications: ['ISO9001'], recommended: false },
        { supplier: '义乌三区·恒达日用', product: '一次性餐具', district: '三区', moq: 2000, unit_price: '¥0.35', delivery_days: 5, rating: 4.5, certifications: ['FDA', 'CE'], recommended: true },
      ],
      logistics: {
        source: '义新欧班列', total_routes: 19, countries_covered: 50, cities_connected: 160,
        routes: [
          { name: '义乌-杜伊斯堡', days: 14, frequency: '每周3班', cost_20ft: '$2,800' },
          { name: '义乌-马德里', days: 21, frequency: '每周3班', cost_20ft: '$2,800' },
          { name: '义乌-伦敦', days: 18, frequency: '每周2班', cost_20ft: '$3,200' },
        ],
        advantages: ['比海运快2-3倍', '比空运便宜60-80%', '通关便利化', '固定班期稳定可靠'],
      },
      trade_1039: {
        applicable: true, name: '市场采购贸易方式（1039）',
        advantages: ['免征增值税，不办理出口退税', '简化报关流程，实行简化申报', '允许多主体收汇，支持人民币结算', '通关便利化，查验率低'],
      },
    },
    content_generation: {
      product_name: '厨房收纳架', category: '日用百货', platform: 'amazon', target_language: 'en',
      content: {
        title: '厨房收纳架 | 义乌直供 | 品质保障 | 义新欧班列直达',
        description: '精选义乌优质厨房收纳架，源自义乌国际商贸城直供。品质可靠，价格优势明显，支持1039市场采购贸易。义新欧班列14天直达欧洲，物流便捷高效。小批量起订，灵活采购，适合跨境电商卖家。',
        seo_keywords: ['厨房收纳架', '义乌直供', '跨境优选', '义新欧直达', '1039市场采购', '品质保障'],
      },
      marketing: {
        social_copy: {
          hook: '还在为厨房收纳发愁？',
          pain_point: '厨房杂乱无章，找不到合适收纳方案',
          solution: '来自义乌的优质厨房收纳架，价格低至1折起，品质保障',
          cta: '点击链接，限时优惠！',
          hashtags: ['#义乌好货', '#厨房收纳架', '#跨境优选', '#义新欧直达'],
        },
      },
      platform_compliance: {
        warnings: ['请确保产品图片符合Amazon规范', '建议添加多语言产品描述', '注意目标市场CE认证要求'],
      },
    },
    compliance: {
      category: '日用百货', target_country: '德国',
      certifications: [
        { name: 'CE认证', required: true, estimated_time: '4-8周', estimated_cost: '¥5,000-50,000' },
        { name: 'RoHS认证', required: true, estimated_time: '2-4周', estimated_cost: '¥3,000-15,000' },
        { name: 'REACH注册', required: true, estimated_time: '2-6周', estimated_cost: '¥2,000-20,000' },
        { name: 'WEEE注册', required: false, estimated_time: '4-8周', estimated_cost: '¥8,000-30,000' },
      ],
      tariff: { tariff_rate: '8%', total_tax: '¥3,000' },
      trade_1039: {
        applicable: true,
        advantages: ['免征增值税，无需取得进项发票', '简化申报，归并商品编码', '通关便利化，优先查验放行'],
      },
      tariff_benefits: {
        description: '义新欧班列运输的货物可享受中欧班列通关便利化政策',
        benefits: ['铁路运输货物通关优先查验', '中欧班列沿线海关互认AEO企业', '1039市场采购贸易简化申报'],
      },
      rcep_benefits: { description: 'RCEP协定下，中国-东盟90%以上税目最终零关税，中欧暂无RCEP优惠但可通过1039模式降低合规成本' },
    },
    customer_service: {
      faqs: [
        { question: '日用百货出口欧盟需要什么认证？', answer: '需符合CE认证、REACH法规，部分产品需RoHS认证。建议提前做好产品检测，选择合规供应商。义乌市场内有专业认证服务机构。' },
        { question: '1039模式如何操作？', answer: '步骤：1)在市场采购贸易综合管理系统备案 2)在试点市场采购商品 3)简化申报出口 4)在线收结汇。单票15万美元以下，可免征增值税。' },
        { question: '义新欧班列运费多少？', answer: '约0.5-0.8美元/kg，比海运快2倍，比空运便宜60-80%。义乌-杜伊斯堡14天，义乌-马德里21天。20尺柜约$2,800。' },
        { question: '如何处理售后纠纷？', answer: '保留证据→联系供应商协商→义乌市商务局投诉→必要时通过仲裁解决。建议签订书面合同，明确售后条款。1039模式下可享受贸易纠纷调解服务。' },
      ],
    },
    policy_replication: {
      total_cities: 39,
      key_points: [
        { title: '增值税免征不退', description: '市场采购贸易出口货物免征增值税，无需取得增值税专用发票即可出口，大幅降低合规成本', benefit_level: '高' },
        { title: '简化申报', description: '实行"简化申报"制度，商品编码归并申报，单票报关单商品项数缩减至5项以内', benefit_level: '高' },
        { title: '通关便利化', description: '享受海关优先查验、快速放行，出口通关时间压缩60%以上', benefit_level: '高' },
        { title: '跨境人民币结算', description: '允许以人民币计价结算，规避汇率风险，简化外汇核销手续', benefit_level: '中' },
        { title: '组柜拼箱', description: '允许多商户货物组柜拼箱出口，降低物流成本，适合小批量多品种出口', benefit_level: '中' },
      ],
      tax_benefits: {
        vat_exemption: true,
        income_tax: '按核定征收，应税所得率统一按5%核定',
        stamp_duty: '免征',
      },
      cases: [
        { title: '义乌饰品出海中东', category: '饰品配件', target_market: '中东（阿联酋、沙特）', annual_export: '1200万美元' },
        { title: '义乌玩具出口东南亚', category: '玩具', target_market: '东南亚（印尼、泰国）', annual_export: '800万美元' },
        { title: '义乌日用百货出口欧洲', category: '日用百货', target_market: '欧洲（德国、法国）', annual_export: '2500万美元' },
      ],
    },
  },
  summary: { total_steps: 7, steps_completed: 7, duration_seconds: 12.5, errors: 0, product: '厨房收纳架' },
});

// ==================== 政策复制 Mock ====================
export const mockPolicyCities = () => ({
  total: 39,
  cities: [
    { city: '义乌', province: '浙江', approved_year: '2013', main_categories: '日用百货、饰品配件、玩具、工艺品', policy_benefits: '增值税免征、简化申报、通关便利化', customs_code: '3313' },
    { city: '海宁', province: '浙江', approved_year: '2016', main_categories: '皮革制品、经编面料、袜子', policy_benefits: '增值税免征、简化申报、跨境人民币结算', customs_code: '3314' },
    { city: '广州', province: '广东', approved_year: '2016', main_categories: '服装、皮具、电子产品', policy_benefits: '增值税免征、简化申报、广交会资源', customs_code: '4401' },
    { city: '深圳', province: '广东', approved_year: '2016', main_categories: '电子产品、智能硬件、珠宝', policy_benefits: '增值税免征、简化申报、前海政策叠加', customs_code: '4403' },
    { city: '成都', province: '四川', approved_year: '2016', main_categories: '鞋类、家具、茶叶', policy_benefits: '增值税免征、简化申报、中欧班列直达', customs_code: '5101' },
    { city: '重庆', province: '重庆', approved_year: '2016', main_categories: '汽摩配件、电子产品、农产品', policy_benefits: '增值税免征、简化申报、渝新欧班列直达', customs_code: '5001' },
    { city: '泉州', province: '福建', approved_year: '2016', main_categories: '鞋服、石材、工艺品', policy_benefits: '增值税免征、简化申报、对台贸易便利', customs_code: '3505' },
    { city: '厦门', province: '福建', approved_year: '2016', main_categories: '电子产品、石材、茶叶', policy_benefits: '增值税免征、简化申报、自贸区叠加优惠', customs_code: '3502' },
    { city: '长沙', province: '湖南', approved_year: '2016', main_categories: '工程机械配件、烟花鞭炮、茶叶', policy_benefits: '增值税免征、简化申报、湘欧快线', customs_code: '4301' },
    { city: '西安', province: '陕西', approved_year: '2016', main_categories: '农产品、工艺品、机械设备', policy_benefits: '增值税免征、简化申报、长安号班列', customs_code: '6101' },
    { city: '郑州', province: '河南', approved_year: '2016', main_categories: '服装、建材、农产品', policy_benefits: '增值税免征、简化申报、郑欧班列', customs_code: '4101' },
    { city: '武汉', province: '湖北', approved_year: '2016', main_categories: '光电子产品、汽车配件、纺织', policy_benefits: '增值税免征、简化申报、汉欧班列', customs_code: '4201' },
  ],
});

export const mockPolicyGuide = () => ({
  policy_name: '市场采购贸易方式（海关监管代码1039）',
  policy_code: '1039',
  background: '为解决小商品出口"多品种、多批次、小批量"的贸易特点，国务院于2013年在义乌率先试点市场采购贸易方式，后在39个城市推广复制',
  key_points: [
    { title: '增值税免征不退', description: '市场采购贸易出口货物免征增值税，且不办理退税。经营者无需取得增值税专用发票即可出口，大幅降低合规成本', benefit_level: '高' },
    { title: '简化申报', description: '实行"简化申报"制度，对商品编码实行"归并申报"，将多个小商品归并为一个大类申报，单票报关单商品项数由数十项缩减至5项以内', benefit_level: '高' },
    { title: '通关便利化', description: '享受海关优先查验、快速放行等便利措施，出口通关时间压缩60%以上，实现"秒放"通关', benefit_level: '高' },
    { title: '跨境人民币结算', description: '允许以人民币计价结算，规避汇率风险，简化外汇核销手续', benefit_level: '中' },
    { title: '组柜拼箱', description: '允许多个商户的货物组柜拼箱出口，降低物流成本，适合小批量多品种的出口模式', benefit_level: '中' },
    { title: '在线收结汇', description: '通过联网信息平台实现在线收结汇，资金到账速度快，结算效率高', benefit_level: '中' },
  ],
  applicable_conditions: [
    '在经认定的市场采购贸易试点区域内采购',
    '经由海关监管的采购地出口',
    '单票报关单商品货值15万美元（含）以下',
    '在市场采购贸易综合管理系统中备案',
    '出口商品不属于禁止出口商品',
  ],
  operation_process: [
    { step: 1, title: '备案登记', description: '在市场采购贸易综合管理系统中完成经营主体备案登记' },
    { step: 2, title: '商品采购', description: '在试点市场内采购商品，取得供货商户信息' },
    { step: 3, title: '组货装箱', description: '在指定监管场所完成组货装箱，生成装箱清单' },
    { step: 4, title: '简化申报', description: '通过综合管理系统进行简化申报，归并商品编码' },
    { step: 5, title: '海关查验', description: '海关实施便利化查验，优先放行' },
    { step: 6, title: '出口通关', description: '货物出口，完成通关手续' },
    { step: 7, title: '收结汇', description: '通过联网信息平台在线收结汇' },
  ],
  tax_benefits: {
    vat_exemption: true,
    vat_description: '出口货物免征增值税，无需取得增值税专用发票',
    income_tax: '按核定征收，应税所得率统一按5%核定',
    stamp_duty: '免征',
    compared_to_general_trade: {
      general_trade_vat: '需取得增值税专用发票，退税率0%-13%',
      market_purchase_vat: '直接免征，无需发票',
      cost_saving: '每100万元出口额可节省合规成本约2-5万元',
    },
  },
});

export const mockPolicyBenefit = (annual_export: number, category: string, city: string) => {
  const vatSaving = Math.round(annual_export * 0.13);
  const complianceSaving = Math.round(annual_export * 0.025);
  const logisticsSaving = Math.round(annual_export * 0.05);
  const totalSaving = vatSaving + complianceSaving + logisticsSaving;
  const generalTradeCost = Math.round(annual_export * 1.18);
  const marketPurchaseCost = generalTradeCost - totalSaving;

  return {
    annual_export,
    category,
    city,
    benefits: {
      vat: { description: '增值税免征', amount: vatSaving, detail: '免征13%增值税，无需取得进项发票' },
      compliance: { description: '合规成本节省', amount: complianceSaving, detail: '简化申报，归并商品编码，合规成本降低80%' },
      logistics: { description: '物流成本节省', amount: logisticsSaving, detail: '组柜拼箱+义新欧班列，物流成本降低30%' },
      time: { description: '通关时间节省', amount: 2, detail: '通关时间从3天压缩至1天，效率提升60%' },
    },
    total_saving: totalSaving,
    saving_rate: `${((totalSaving / generalTradeCost) * 100).toFixed(1)}%`,
    compared_to_general_trade: {
      general_trade_total_cost: generalTradeCost,
      market_purchase_total_cost: marketPurchaseCost,
      cost_reduction: `${((totalSaving / generalTradeCost) * 100).toFixed(1)}%`,
    },
  };
};

export const mockPolicyCases = () => ({
  cases: [
    {
      case_id: 1,
      title: '义乌饰品出海中东——从个体户到千万出口商',
      category: '饰品配件',
      target_market: '中东（阿联酋、沙特）',
      annual_export: '1200万美元',
      key_strategies: ['利用1039模式简化申报，将200+SKU饰品归并为5大类出口', '通过义新欧班列+中东航线组合物流，运输成本降低30%', '利用免征增值税政策，无需取得进项发票，合规成本降低80%'],
      localization_tips: ['中东市场偏好金色、大尺寸饰品，需调整产品规格', '包装需符合清真认证要求', '建立当地仓储，实现48小时配送'],
      replication_difficulty: '中等',
      replicable_points: ['1039简化申报模式可直接复制', '组柜拼箱降低物流成本的经验可复制', '免征增值税政策在39城均可享受'],
    },
    {
      case_id: 2,
      title: '义乌玩具出口东南亚——RCEP+1039双政策红利',
      category: '玩具',
      target_market: '东南亚（印尼、泰国、越南）',
      annual_export: '800万美元',
      key_strategies: ['叠加RCEP关税优惠和1039增值税免征双重政策红利', '通过跨境人民币结算规避汇率风险', '利用在线收结汇平台，资金周转效率提升50%'],
      localization_tips: ['东南亚市场偏好益智类和户外类玩具', '需取得当地安全认证（如印尼SNI认证）', '建立本地化客服团队，提供多语言服务'],
      replication_difficulty: '较低',
      replicable_points: ['RCEP+1039双政策叠加模式可在沿海城市复制', '跨境人民币结算在所有试点城市可用', '在线收结汇平台已全国联网'],
    },
    {
      case_id: 3,
      title: '义乌日用百货出口欧洲——义新欧班列+1039模式',
      category: '日用百货',
      target_market: '欧洲（德国、法国、西班牙）',
      annual_export: '2500万美元',
      key_strategies: ['利用义新欧班列直达欧洲，比海运快2-3倍、比空运便宜60-80%', '1039模式通关便利化，出口通关时间压缩60%', '组柜拼箱模式，多商户共享集装箱，物流成本降低40%'],
      localization_tips: ['欧洲市场注重环保，需符合REACH法规', '产品包装需使用可回收材料', '建立欧洲海外仓，实现本地化配送'],
      replication_difficulty: '中等',
      replicable_points: ['义新欧班列沿线城市均可复制此模式', '1039通关便利化在所有试点城市适用', '组柜拼箱模式可在商贸城集群城市推广'],
    },
  ],
});
