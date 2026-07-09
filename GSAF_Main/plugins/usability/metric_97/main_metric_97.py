"""
Factor 97

Site Updates / Maintenance
"""

from utils.core.base_seo_plugin import BaseSEOPlugin


class SiteUpdatesPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "97 - Site Updates"

    def run(self):
        result = self.create_result()
        response, _ = self.fetch_html()

        score = 100 if response.headers.get("last-modified") else 50
        self.set_score(result, score)
        result.update({
            "last_modified_header": response.headers.get("last-modified", ""),
            "status_code": response.status_code,
        })
        return result
