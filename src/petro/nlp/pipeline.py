"""NLP processing pipeline for news articles."""

from typing import Any, Dict, Optional

from petro.core import get_logger
from petro.nlp.cleaner import NewsClener
from petro.nlp.classifier import NewsClassifier
from petro.nlp.deduplicator import NewsDeduplicator
from petro.nlp.lang_detector import LanguageDetector
from petro.nlp.ner import NamedEntityRecognizer
from petro.nlp.sentiment import SentimentAnalyzer

logger = get_logger(__name__)


class NewsProcessingPipeline:
    """Complete NLP pipeline for processing news articles."""

    def __init__(self):
        """Initialize all NLP components."""
        self.cleaner = NewsClener()
        self.deduplicator = NewsDeduplicator()
        self.lang_detector = LanguageDetector()
        self.ner = NamedEntityRecognizer()
        self.classifier = NewsClassifier()
        self.sentiment = SentimentAnalyzer()

    async def process_single(self, title: str, content: str) -> Optional[Dict[str, Any]]:
        """Process a single news article through the complete pipeline.

        Args:
            title: News title
            content: News content

        Returns:
            Dictionary with processed news data or None on critical failure
        """
        try:
            # Step 1: Clean text
            cleaned_title = self.cleaner.clean_text(title)
            cleaned_content = self.cleaner.clean_text(content)

            if not cleaned_content:
                logger.warning("Empty content after cleaning")
                return None

            # Step 2: Detect language
            language = self.lang_detector.detect_language(cleaned_content)
            if not language:
                logger.warning("Could not detect language, defaulting to es")
                language = "es"

            # Step 3: Extract entities
            entities = self.ner.extract_entities(cleaned_content, language)

            # Step 4: Extract keywords
            keywords = self.ner.extract_keywords(cleaned_content, language)

            # Step 5: Classify news
            classification = self.classifier.classify(cleaned_content)
            classification_detail = self.classifier.classify_with_confidence(cleaned_content)

            # Step 6: Analyze sentiment
            sentiment_result = self.sentiment.analyze_with_score(cleaned_content)

            # Compile results
            result = {
                "title": cleaned_title,
                "content": cleaned_content,
                "language": language,
                "entities": entities,
                "keywords": keywords,
                "classification": classification,
                "classification_detail": classification_detail,
                "sentiment": sentiment_result,
            }

            logger.debug(f"Processed article: {cleaned_title[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error processing article: {e}", exc_info=True)
            return None

    async def process_batch(self, articles: list) -> list:
        """Process batch of articles.

        Args:
            articles: List of {title, content} dictionaries

        Returns:
            List of processed articles
        """
        results = []

        for article in articles:
            try:
                processed = await self.process_single(
                    article.get("title", ""),
                    article.get("content", ""),
                )
                if processed:
                    results.append(processed)
            except Exception as e:
                logger.error(f"Error processing article in batch: {e}")

        logger.info(f"Processed {len(results)}/{len(articles)} articles")
        return results

    async def deduplicate_batch(self, titles: list, threshold: float = 0.85) -> tuple:
        """Remove duplicates from batch of news titles.

        Args:
            titles: List of news titles
            threshold: Similarity threshold

        Returns:
            Tuple of (unique_titles, kept_indices)
        """
        try:
            unique, indices = self.deduplicator.deduplicate_batch(titles, threshold)
            logger.info(f"Deduplicated {len(titles)} titles to {len(unique)} unique")
            return unique, indices
        except Exception as e:
            logger.error(f"Error deduplicating batch: {e}")
            return titles, list(range(len(titles)))

    def _sentiment_to_score(self, sentiment_result: Optional[dict]) -> Optional[float]:
        """Convert sentiment result to -1 to 1 score.

        Args:
            sentiment_result: Sentiment analysis result

        Returns:
            Score from -1 to 1, or None
        """
        if not sentiment_result:
            return None

        return sentiment_result.get("score")
