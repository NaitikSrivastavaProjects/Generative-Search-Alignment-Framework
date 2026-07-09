"""
URL Utilities
"""

from urllib.parse import urlparse


class URLUtils:

    @staticmethod
    def clean_domain(url):

        parsed = urlparse(url)

        domain = parsed.netloc.lower()

        if domain.startswith("www."):

            domain = domain[4:]

        return domain

    @staticmethod
    def is_https(url):

        return url.lower().startswith(
            "https://"
        )