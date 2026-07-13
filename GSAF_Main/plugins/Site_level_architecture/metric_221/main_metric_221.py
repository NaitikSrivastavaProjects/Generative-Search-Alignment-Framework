"""
Factor 221

User Reviews / Site Reputation
"""

from utils.core.base_seo_plugin import BaseSEOPlugin
from utils.helpers import get_link_targets


class SiteReputationPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "221 - Site Reputation"

    def run(self):
        result = self.create_result()
        _, soup = self.fetch_html()
        links = get_link_targets(soup, self.url)

        reputation_found = any(
            "trustpilot" in link["href"].lower() or "bbb" in link["href"].lower() or "review" in link["text"].lower()
            for link in links
        )
        score = 100 if reputation_found else 0
        self.set_score(result, score)
        result.update({
            "reputation_links_found": reputation_found,
            "links_checked": len(links),
        })
        return result
