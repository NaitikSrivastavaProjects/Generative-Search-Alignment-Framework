"""
Factor 107

Site Usability
"""

from core.base_seo_plugin import BaseSEOPlugin
from utils.helpers import get_link_targets


class SiteUsabilityPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "107 - Site Usability"

    def run(self):
        result = self.create_result()
        _, soup = self.fetch_html()
        links = get_link_targets(soup, self.url)

        nav_links = [link for link in links if len(link["text"].split()) <= 3]
        score = 70 if nav_links else 30
        self.set_score(result, score)
        result.update({
            "navigation_links_found": len(nav_links),
            "total_links_found": len(links),
        })
        return result
