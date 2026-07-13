"""
Factor 218

Mobile Optimization
"""

from utils.core.base_seo_plugin import BaseSEOPlugin
from utils.helpers import extract_text


class MobileOptimizationPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "218 - Mobile Optimization"

    def run(self):
        result = self.create_result()
        _, soup = self.fetch_html()

        viewport = soup.find("meta", attrs={"name": "viewport"})
        responsive_score = 50 if viewport else 0
        text = extract_text(soup)
        has_content = bool(text.strip())

        score = responsive_score + (50 if has_content else 0)
        self.set_score(result, score)
        result.update({
            "viewport_meta_found": bool(viewport),
            "has_content": has_content,
        })
        return result
