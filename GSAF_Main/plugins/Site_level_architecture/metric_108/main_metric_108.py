"""
Factor 108

Google Analytics & Search Console
"""

from utils.core.base_seo_plugin import BaseSEOPlugin


class GoogleAnalyticsPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "108 - Google Analytics & Search Console"

    def run(self):
        result = self.create_result()
        _, soup = self.fetch_html()

        analytics_found = False
        search_console_found = False
        for tag in soup.find_all(["meta", "script", "link"]):
            attrs = " ".join(str(tag.attrs).lower() for tag in [tag])
            if "googletagmanager" in attrs or "gtag" in attrs:
                analytics_found = True
            if "google-site-verification" in attrs or "search-console" in attrs:
                search_console_found = True

        score = 100 if analytics_found and search_console_found else 70 if analytics_found or search_console_found else 0
        self.set_score(result, score)
        result.update({
            "google_analytics_found": analytics_found,
            "google_search_console_found": search_console_found,
        })
        return result
