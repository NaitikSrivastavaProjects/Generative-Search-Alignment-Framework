"""
Factor 95

Domain Trust
"""

from urllib.parse import urlparse

from core.base_seo_plugin import BaseSEOPlugin


class DomainTrustPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "95 - Domain Trust"

    def run(self):
        result = self.create_result()
        response, _ = self.fetch_html()

        domain = urlparse(self.url).netloc.lower()
        secure = response.url.startswith("https")
        score = 70 if secure and len(domain) > 5 else 40 if domain else 0
        self.set_score(result, score)
        result.update({
            "domain": domain,
            "https_enabled": secure,
        })
        return result
