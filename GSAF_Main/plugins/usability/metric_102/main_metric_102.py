"""
Factor 102

Terms of Service & Privacy Pages
"""

from utils.core.base_seo_plugin import BaseSEOPlugin
from utils.keywords import PRIVACY_KEYWORDS, TERMS_KEYWORDS
from utils.helpers import get_link_targets


class TermsPrivacyPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "102 - Terms of Service & Privacy Pages"

    def run(self):
        result = self.create_result()
        _, soup = self.fetch_html()
        links = get_link_targets(soup, self.url)

        privacy_found = any(
            keyword in link["text"] or keyword in link["href"]
            for link in links
            for keyword in PRIVACY_KEYWORDS
        )
        terms_found = any(
            keyword in link["text"] or keyword in link["href"]
            for link in links
            for keyword in TERMS_KEYWORDS
        )

        score = 0
        if privacy_found:
            score += 50
        if terms_found:
            score += 50

        self.set_score(result, score)
        result.update({
            "privacy_page_found": privacy_found,
            "terms_page_found": terms_found,
            "links_checked": len(links),
        })
        return result
