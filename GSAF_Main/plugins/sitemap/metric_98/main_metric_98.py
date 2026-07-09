"""
Factor 98

Sitemap Availability
"""

from utils.core.base_seo_plugin import BaseSEOPlugin
from utils.keywords import SITEMAP_KEYWORDS
from utils.helpers import get_link_targets


class SitemapAvailabilityPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "98 - Sitemap Availability"

    def run(self):
        result = self.create_result()
        _, soup = self.fetch_html()
        links = get_link_targets(soup, self.url)

        sitemap_found = any(
            keyword in link["text"] or keyword in link["href"]
            for link in links
            for keyword in SITEMAP_KEYWORDS
        )
        score = 100 if sitemap_found else 0
        self.set_score(result, score)
        result.update({
            "sitemap_found": sitemap_found,
            "links_checked": len(links),
        })
        return result
