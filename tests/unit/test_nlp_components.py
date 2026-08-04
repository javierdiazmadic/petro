"""Unit tests for NLP components."""

import pytest

from petro.nlp.cleaner import NewsClener
from petro.nlp.deduplicator import NewsDeduplicator
from petro.nlp.lang_detector import LanguageDetector


class TestNewsCleaner:
    """Tests for NewsClener."""

    def test_strip_html(self):
        """Test HTML tag removal."""
        html = "<p>Hello <b>world</b></p>"
        result = NewsClener.strip_html(html)
        assert result == "Hello world"

    def test_strip_html_empty(self):
        """Test empty HTML."""
        result = NewsClener.strip_html("")
        assert result == ""

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "Hello   world  \n  test"
        result = NewsClener.normalize_whitespace(text)
        assert result == "Hello world test"

    def test_remove_urls(self):
        """Test URL removal."""
        text = "Check https://example.com for more info"
        result = NewsClener.remove_urls(text)
        assert "https://example.com" not in result
        assert "Check" in result

    def test_remove_email(self):
        """Test email removal."""
        text = "Contact us at info@example.com for details"
        result = NewsClener.remove_email(text)
        assert "info@example.com" not in result

    def test_clean_text_complete(self):
        """Test complete cleaning pipeline."""
        html = "<p>Visit https://oil.news.com or email info@oil.com</p>"
        result = NewsClener.clean_text(html)
        assert "<p>" not in result
        assert "https://" not in result
        assert "@" not in result
        assert "Visit" in result


class TestNewsDeduplicator:
    """Tests for NewsDeduplicator."""

    def test_hash_title(self):
        """Test title hashing."""
        title = "Oil Prices Rise"
        hash1 = NewsDeduplicator.hash_title(title)
        hash2 = NewsDeduplicator.hash_title(title)
        assert hash1 == hash2

    def test_hash_title_case_insensitive(self):
        """Test that hashing is case-insensitive."""
        hash1 = NewsDeduplicator.hash_title("Oil Prices Rise")
        hash2 = NewsDeduplicator.hash_title("oil prices rise")
        assert hash1 == hash2

    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculation."""
        assert NewsDeduplicator.levenshtein_distance("", "") == 0
        assert NewsDeduplicator.levenshtein_distance("a", "") == 1
        assert NewsDeduplicator.levenshtein_distance("abc", "abc") == 0
        assert NewsDeduplicator.levenshtein_distance("abc", "ab") == 1

    def test_similarity_score(self):
        """Test similarity score calculation."""
        # Identical
        assert NewsDeduplicator.similarity_score("test", "test") == 1.0

        # Completely different
        assert NewsDeduplicator.similarity_score("aaa", "bbb") == 0.0

        # Partially similar
        score = NewsDeduplicator.similarity_score("oil", "oils")
        assert 0.5 < score < 1.0

    def test_is_duplicate(self):
        """Test duplicate detection."""
        assert NewsDeduplicator.is_duplicate("Oil prices rise", "Oil prices rise", threshold=0.95)
        assert not NewsDeduplicator.is_duplicate("Oil prices", "Gas prices", threshold=0.9)

    def test_deduplicate_batch(self):
        """Test batch deduplication."""
        titles = [
            "Oil Prices Rise",
            "Oil Prices Rise Today",  # Likely duplicate
            "Gas Prices Fall",
        ]
        unique, indices = NewsDeduplicator.deduplicate_batch(titles, threshold=0.85)
        assert len(unique) <= len(titles)
        assert len(indices) == len(unique)


class TestLanguageDetector:
    """Tests for LanguageDetector."""

    def test_detect_spanish(self):
        """Test Spanish language detection."""
        text = "Los precios del petróleo han subido significativamente en los últimos días"
        lang = LanguageDetector.detect_language(text)
        assert lang == "es"

    def test_detect_english(self):
        """Test English language detection."""
        text = "Oil prices have risen significantly in recent days"
        lang = LanguageDetector.detect_language(text)
        assert lang == "en"

    def test_detect_too_short_text(self):
        """Test that very short text returns None."""
        lang = LanguageDetector.detect_language("oil")
        assert lang is None

    def test_is_supported_language(self):
        """Test language support checking."""
        assert LanguageDetector.is_supported_language("es")
        assert LanguageDetector.is_supported_language("en")
        assert not LanguageDetector.is_supported_language("xx")
