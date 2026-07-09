"""
Factor 94

Contact Us Page
"""

import re
from urllib.parse import urljoin

from utils.core.base_seo_plugin import BaseSEOPlugin


class ContactUsPlugin(
    BaseSEOPlugin
):

    @property
    def factor(self):

        return (
            "94 - Contact Us Page"
        )

    def run(self):

        result = self.create_result()

        response, soup = (
            self.fetch_html()
        )

        links = soup.find_all(
            "a",
            href=True
        )

        contact_found = False

        for link in links:

            text = link.get_text(
                strip=True
            ).lower()

            href = link[
                "href"
            ].lower()

            if (
                "contact" in text
                or "contact" in href
            ):

                contact_found = True

                result.add(
                    "contact_page",
                    urljoin(
                        self.url,
                        link["href"]
                    )
                )

                break

        page = soup.get_text(" ")

        email = re.search(

            r"[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\."
            r"[A-Za-z]{2,}",

            page

        )

        phone = re.search(

            r"\+?\d[\d\s\-\(\)]{7,}",

            page

        )

        score = 0

        if contact_found:
            score += 40

        if email:
            score += 30

        if phone:
            score += 30

        self.set_score(
            result,
            score
        )

        result.update({

            "contact_found":
                contact_found,

            "email_found":
                bool(email),

            "phone_found":
                bool(phone)

        })

        return result