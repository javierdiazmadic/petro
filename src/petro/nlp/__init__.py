"""NLP module for news processing."""

from petro.nlp.classifier import NewsClassifier
from petro.nlp.cleaner import NewsClener
from petro.nlp.deduplicator import NewsDeduplicator
from petro.nlp.lang_detector import LanguageDetector
from petro.nlp.ner import NamedEntityRecognizer
from petro.nlp.pipeline import NewsProcessingPipeline
from petro.nlp.sentiment import SentimentAnalyzer

__all__ = [
    "NewsClener",
    "NewsDeduplicator",
    "LanguageDetector",
    "NamedEntityRecognizer",
    "NewsClassifier",
    "SentimentAnalyzer",
    "NewsProcessingPipeline",
]
