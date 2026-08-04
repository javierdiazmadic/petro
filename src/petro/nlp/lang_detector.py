"""Language detection for news articles."""

from typing import Optional

import langdetect

from petro.core import get_logger

logger = get_logger(__name__)

# Language codes
SPANISH = "es"
ENGLISH = "en"
FRENCH = "fr"
PORTUGUESE = "pt"
GERMAN = "de"

SUPPORTED_LANGUAGES = [SPANISH, ENGLISH, FRENCH, PORTUGUESE, GERMAN]


class LanguageDetector:
    """Detects language of news articles."""

    @staticmethod
    def detect_language(text: str) -> Optional[str]:
        """Detect language of text.

        Args:
            text: Text to detect language for

        Returns:
            Language code (es, en, fr, etc) or None if detection fails
        """
        if not text or len(text) < 10:
            logger.debug("Text too short for language detection")
            return None

        try:
            detected = langdetect.detect(text)
            return detected if detected in SUPPORTED_LANGUAGES else None

        except Exception as e:
            logger.warning(f"Error detecting language: {e}")
            return None

    @staticmethod
    def detect_probabilities(text: str) -> Optional[dict]:
        """Detect language with probability scores.

        Args:
            text: Text to detect language for

        Returns:
            Dictionary with language probabilities, or None on error
        """
        if not text or len(text) < 10:
            return None

        try:
            probabilities = langdetect.detect_langs(text)
            result = {}
            for prob in probabilities:
                if prob.lang in SUPPORTED_LANGUAGES:
                    result[prob.lang] = round(prob.prob, 3)
            return result if result else None

        except Exception as e:
            logger.warning(f"Error detecting language probabilities: {e}")
            return None

    @staticmethod
    def is_supported_language(language: str) -> bool:
        """Check if language is supported.

        Args:
            language: Language code

        Returns:
            True if language is supported
        """
        return language in SUPPORTED_LANGUAGES
