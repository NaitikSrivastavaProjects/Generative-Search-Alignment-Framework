"""
Factor 106

YouTube Integration
"""

from utils.core.base_seo_plugin import BaseSEOPlugin


class YouTubeIntegrationPlugin(BaseSEOPlugin):

    @property
    def factor(self):
        return "106 - YouTube Integration"

    def run(self):
        result = self.create_result()
        _, soup = self.fetch_html()

        youtube_embeds = soup.find_all("iframe", src=True)
        youtube_found = any("youtube.com" in iframe["src"].lower() for iframe in youtube_embeds)
        score = 100 if youtube_found else 0
        self.set_score(result, score)
        result.update({
            "youtube_embed_found": youtube_found,
            "iframe_count": len(youtube_embeds),
        })
        return result
