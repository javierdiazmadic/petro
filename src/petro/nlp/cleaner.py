"""News content cleaning and normalization."""

import re
from html.parser import HTMLParser
from typing import Optional

from petro.core import get_logger

logger = get_logger(__name__)


class MLStripper(HTMLParser):
    """HTML tag stripper."""

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_data(self):
        return "".join(self.text)


class NewsClener:
    """Cleans and normalizes news content."""

    @staticmethod
    def strip_html(html: str) -> str:
        """Remove HTML tags from text.

        Args:
            html: HTML content

        Returns:
            Plain text without HTML tags
        """
        if not html:
            return ""

        try:
            stripper = MLStripper()
            stripper.feed(html)
            return stripper.get_data()
        except Exception as e:
            logger.warning(f"Error stripping HTML: {e}")
            return html

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace and newlines.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text.

        Args:
            text: Text containing URLs

        Returns:
            Text without URLs
        """
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        return re.sub(url_pattern, "", text)

    @staticmethod
    def remove_email(text: str) -> str:
        """Remove email addresses from text.

        Args:
            text: Text containing emails

        Returns:
            Text without emails
        """
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.sub(email_pattern, "", text)

    @staticmethod
    def remove_extra_punctuation(text: str) -> str:
        """Remove extra punctuation and special characters.

        Args:
            text: Text with extra punctuation

        Returns:
            Cleaned text
        """
        # Remove consecutive punctuation
        text = re.sub(r"[!?]{2,}", "!", text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r"[^\w\s.,!?'-]", "", text)
        return text

    @staticmethod
    def clean_text(text: str, strip_urls: bool = True, strip_email: bool = True) -> str:
        """Complete text cleaning pipeline.

        Args:
            text: Raw text
            strip_urls: Whether to remove URLs
            strip_email: Whether to remove emails

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Strip HTML
        text = NewsClener.strip_html(text)

        # Remove URLs
        if strip_urls:
            text = NewsClener.remove_urls(text)

        # Remove emails
        if strip_email:
            text = NewsClener.remove_email(text)

        # Normalize whitespace
        text = NewsClener.normalize_whitespace(text)

        # Remove extra punctuation
        text = NewsClener.remove_extra_punctuation(text)

        return text
