"""
Factor 99

Site Uptime
"""

from core.base_seo_plugin import BaseSEOPlugin


class SiteUptimePlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "99 - Site Uptime"

    def run(self):
        result = self.create_result()
        response, _ = self.fetch_html()
        score = 100 if response.status_code < 400 else 0
        self.set_score(result, score)
        result.update({
            "status_code": response.status_code,
        })
        return result
