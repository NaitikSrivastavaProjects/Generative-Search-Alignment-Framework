"""
Factor 208

Site Architecture
"""

from utils.core.base_seo_plugin import BaseSEOPlugin
from utils.helpers import get_link_targets, is_internal_link


class SiteArchitecturePlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "208- Site Architecture"

    def run(self):
        result = self.create_result()
        _, soup = self.fetch_html()
        links = get_link_targets(soup, self.url)
        internal_links = [link for link in links if is_internal_link(link["href"], self.url)]

        score = 100 if len(internal_links) >= 5 else 50 if internal_links else 0
        self.set_score(result, score)
        result.update({
            "internal_links_found": len(internal_links),
            "total_links_found": len(links),
        })
        return result
