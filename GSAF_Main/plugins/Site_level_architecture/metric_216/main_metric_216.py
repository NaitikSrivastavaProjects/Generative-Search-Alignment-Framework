"""
Factor 216

Duplicate Meta Information
"""

from collections import Counter

from utils.core.base_seo_plugin import BaseSEOPlugin
from utils.helpers import extract_text


class DuplicateMetaPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "216 - Duplicate Meta Information"

    def run(self):
        result = self.create_result()
        _, soup = self.fetch_html()

        titles = [
            tag.get("content", "")
            for tag in soup.find_all("meta")
            if tag.get("name", "").lower() in {"title", "description"}
        ]
        title_texts = [text.strip() for text in titles if text.strip()]
        duplicates = [item for item, count in Counter(title_texts).items() if count > 1]

        score = 100 if not duplicates else 40
        self.set_score(result, score)
        result.update({
            "duplicate_meta_found": bool(duplicates),
            "duplicate_values": duplicates,
            "meta_texts_checked": len(title_texts),
            "page_text_preview": extract_text(soup)[:300],
        })
        return result
