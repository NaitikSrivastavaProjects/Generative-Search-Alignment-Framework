"""
Factor 101

SSL Certificate / HTTPS
"""

from core.base_seo_plugin import BaseSEOPlugin
from utils.url_utils import URLUtils


class SSLCertificatePlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "101 - SSL Certificate"

    def run(self):
        result = self.create_result()
        response, _ = self.fetch_html()
        https_enabled = URLUtils.is_https(self.url) or response.url.startswith("https")
        score = 100 if https_enabled else 0
        self.set_score(result, score)
        result.update({
            "https_enabled": https_enabled,
            "final_url": response.url,
        })
        return result
