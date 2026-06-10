"""义乌小商品出海智能体 - 内容生成Agent"""

import random
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..data.market_data import CATEGORY_LIST
from ..data.content_data import (
    SUPPORTED_LANGUAGES, SUPPORTED_PLATFORMS, SEO_KEYWORDS,
    HIGHLIGHT_TEMPLATES, SOCIAL_COPY_TEMPLATES, DESCRIPTION_TEMPLATES,
    TITLE_TEMPLATES, AD_COPY_TEMPLATES,
)


class ContentGenerationAgent(BaseAgent):
    """内容生成Agent - 多语言内容生成、SEO优化、营销文案"""

    name = "content_generation"
    description = "内容生成Agent - 多语言产品标题/描述/卖点/SEO/社媒/广告文案"

    # 品类翻译映射
    CATEGORY_TRANSLATIONS = {
        "日用百货": {"en": "Daily Necessities", "de": "Haushaltswaren", "fr": "Articles Ménagers", "es": "Artículos Diarios", "ar": "مستلزمات يومية", "ru": "Товары повседневного спроса", "kk": "Күнделікті тауарлар", "ja": "日用品"},
        "饰品配件": {"en": "Jewelry & Accessories", "de": "Schmuck & Zubehör", "fr": "Bijoux & Accessoires", "es": "Joyería y Accesorios", "ar": "مجوهرات وإكسسوارات", "ru": "Украшения и аксессуары", "kk": "Әшекей бұйымдар", "ja": "アクセサリー"},
        "玩具": {"en": "Toys", "de": "Spielzeug", "fr": "Jouets", "es": "Juguetes", "ar": "ألعاب", "ru": "Игрушки", "kk": "Ойыншықтар", "ja": "玩具"},
        "文具办公用品": {"en": "Stationery & Office Supplies", "de": "Schreibwaren & Bürobedarf", "fr": "Papeterie & Fournitures", "es": "Papelería y Oficina", "ar": "قرطاسية ومستلزمات مكتبية", "ru": "Канцелярские товары", "kk": "Канцелярия", "ja": "文房具・オフィス用品"},
        "针织品": {"en": "Knitwear", "de": "Strickwaren", "fr": "Tricot", "es": "Punto", "ar": "منتجات تريكو", "ru": "Трикотаж", "kk": "Трикотаж", "ja": "ニット用品"},
        "工艺品": {"en": "Crafts & Decor", "de": "Handwerk & Deko", "fr": "Artisanat & Déco", "es": "Artesanía y Decoración", "ar": "حرف يدوية وديكور", "ru": "Ремесла и декор", "kk": "Қолөнер және декор", "ja": "工芸品"},
        "电子电器": {"en": "Electronics & Electrical", "de": "Elektronik & Elektro", "fr": "Électronique & Électrique", "es": "Electrónica y Eléctrica", "ar": "إلكترونيات وكهربائيات", "ru": "Электроника и электрика", "kk": "Электроника және электр", "ja": "電子電器"},
        "五金工具": {"en": "Hardware & Tools", "de": "Werkzeug & Eisenwaren", "fr": "Quincaillerie & Outils", "es": "Ferretería y Herramientas", "ar": "أدوات ومعدات", "ru": "Инструменты и фурнитура", "kk": "Құралдар және жабдықтар", "ja": "金物・工具"},
        "服装服饰": {"en": "Clothing & Apparel", "de": "Kleidung & Bekleidung", "fr": "Vêtements & Mode", "es": "Ropa y Moda", "ar": "ملابس وأزياء", "ru": "Одежда", "kk": "Киім", "ja": "アパレル"},
        "家居装饰": {"en": "Home Decor", "de": "Heimdekoration", "fr": "Décoration Maison", "es": "Decoración del Hogar", "ar": "ديكور منزلي", "ru": "Домашний декор", "kk": "Үй декоры", "ja": "ホームデコ"},
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        product_name = kwargs.get("product_name", "")
        category = kwargs.get("category", CATEGORY_LIST[0])
        platform = kwargs.get("platform", "amazon")
        target_language = kwargs.get("target_language", "en")

        # 生成内容
        title = self._generate_title(product_name, category, platform, target_language)
        description = self._generate_description(product_name, category, target_language)
        highlights = self._generate_highlights(category)
        seo_keywords = self._generate_seo_keywords(category, target_language)
        social_copy = self._generate_social_copy(category, target_language)
        ad_copy = self._generate_ad_copy(category, target_language)

        # 平台合规提示
        warnings = self._get_platform_warnings(category, platform)

        return self._wrap_response({
            "product_name": product_name,
            "category": category,
            "platform": platform,
            "target_language": target_language,
            "content": {
                "title": title,
                "description": description,
                "highlights": highlights,
                "seo_keywords": seo_keywords,
            },
            "marketing": {
                "social_copy": social_copy,
                "ad_copy": ad_copy,
            },
            "platform_compliance": {
                "warnings": warnings,
            },
        })

    def _generate_title(self, product_name: str, category: str, platform: str, lang: str) -> str:
        """生成产品标题"""
        template = TITLE_TEMPLATES.get(category, "")
        translated_category = self._translate_category(category, lang)
        translated_name = self._translate_product_name(product_name, lang)

        if platform == "amazon":
            return f"{translated_name} - {translated_category} | Yiwu Direct | {template.split('|')[-1].strip() if '|' in template else ''}"
        elif platform == "alibaba":
            return f"Wholesale {translated_name} {translated_category} from Yiwu Market"
        elif platform == "tiktok":
            return f"🔥 {translated_name} {translated_category} #YiwuDirect"
        else:
            return f"{translated_name} | {translated_category} | Yiwu Supply"

    def _generate_description(self, product_name: str, category: str, lang: str) -> str:
        """生成产品描述"""
        template = DESCRIPTION_TEMPLATES.get(category, "")
        if lang != "zh":
            translated_category = self._translate_category(category, lang)
            return f"Premium {translated_category} from Yiwu International Trade City. {template[:100]}... Direct supply, competitive pricing, Yixinou Railway delivery available."
        return template

    def _generate_highlights(self, category: str) -> List[Dict[str, str]]:
        """生成卖点"""
        return HIGHLIGHT_TEMPLATES.get(category, [])

    def _generate_seo_keywords(self, category: str, lang: str) -> List[str]:
        """生成SEO关键词"""
        keywords = SEO_KEYWORDS.get(category, {})
        return keywords.get(lang, keywords.get("en", []))

    def _generate_social_copy(self, category: str, lang: str) -> Dict[str, Any]:
        """生成社媒文案"""
        template = SOCIAL_COPY_TEMPLATES.get(category, {})
        return template

    def _generate_ad_copy(self, category: str, lang: str) -> Dict[str, str]:
        """生成广告文案"""
        return AD_COPY_TEMPLATES.get(category, {"headline": "Yiwu Direct", "body": "From Yiwu to the World", "cta_button": "Shop Now"})

    def _get_platform_warnings(self, category: str, platform: str) -> List[str]:
        """获取平台合规提示"""
        warnings = []
        if platform == "amazon":
            warnings.append("Amazon要求提供产品认证证书(CE/FCC等)")
            warnings.append("需确保产品标签符合目标国语言要求")
        elif platform == "alibaba":
            warnings.append("建议上传工厂认证和产品检测报告")
        elif platform == "tiktok":
            warnings.append("短视频内容需符合平台社区规范")
        return warnings

    def _translate_category(self, category: str, lang: str) -> str:
        """翻译品类名称"""
        translations = self.CATEGORY_TRANSLATIONS.get(category, {})
        return translations.get(lang, category)

    def _translate_product_name(self, name: str, lang: str) -> str:
        """翻译产品名称（简化版）"""
        if lang == "zh" or not name:
            return name
        # 简单映射，实际应调用LLM翻译
        return name
