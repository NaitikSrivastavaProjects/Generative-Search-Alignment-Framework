"""
Factor 104

Breadcrumb Navigation
"""

from core.base_seo_plugin import BaseSEOPlugin


class BreadcrumbNavigationPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "104 - Breadcrumb Navigation"

    def run(self):
        result = self.create_result()
        _, soup = self.fetch_html()

        breadcrumb = soup.find(class_="breadcrumb") or soup.find("nav", attrs={"aria-label": "breadcrumb"})
        score = 100 if breadcrumb else 0
        self.set_score(result, score)
        result.update({
            "breadcrumb_found": bool(breadcrumb),
        })
        return result
