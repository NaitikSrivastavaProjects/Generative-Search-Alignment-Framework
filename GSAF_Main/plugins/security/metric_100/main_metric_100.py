"""
Factor 100

Server Location
"""

from urllib.parse import urlparse

from utils.core.base_seo_plugin import BaseSEOPlugin


class ServerLocationPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "100 - Server Location"

    def run(self):
        result = self.create_result()
        _, _ = self.fetch_html()
        domain = urlparse(self.url).netloc.lower()
        score = 50 if domain else 0
        self.set_score(result, score)
        result.update({
            "domain": domain,
        })
        return result
