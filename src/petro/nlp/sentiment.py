"""Sentiment analysis for news articles."""

from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from petro.core import get_logger

logger = get_logger(__name__)


class SentimentAnalyzer:
    """Analyzes sentiment of news articles."""

    def __init__(self):
        """Initialize sentiment analyzer."""
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2),
            lowercase=True,
        )
        self.classifier = LogisticRegression(max_iter=1000, random_state=42)
        self.is_trained = False

    def train(self, texts: list, sentiments: list) -> bool:
        """Train sentiment analyzer on labeled examples.

        Args:
            texts: List of news texts
            sentiments: List of sentiment labels (-1=negative, 0=neutral, 1=positive)

        Returns:
            True if training successful
        """
        if len(texts) != len(sentiments):
            logger.error("Number of texts must match number of sentiments")
            return False

        # Validate sentiments
        for sentiment in sentiments:
            if sentiment not in [-1, 0, 1]:
                logger.error(f"Invalid sentiment value: {sentiment} (must be -1, 0, or 1)")
                return False

        try:
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, sentiments)
            self.is_trained = True
            logger.info(f"Sentiment analyzer trained on {len(texts)} examples")
            return True

        except Exception as e:
            logger.error(f"Error training sentiment analyzer: {e}")
            return False

    def analyze(self, text: str) -> Optional[int]:
        """Analyze sentiment of text.

        Args:
            text: News text to analyze

        Returns:
            Sentiment score (-1, 0, 1) or None if not trained
        """
        if not self.is_trained or not text:
            return None

        try:
            X = self.vectorizer.transform([text])
            prediction = self.classifier.predict(X)[0]
            return int(prediction)

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return None

    def analyze_with_score(self, text: str) -> Optional[dict]:
        """Analyze sentiment with continuous confidence score.

        Args:
            text: News text to analyze

        Returns:
            Dictionary with sentiment and score [-1, 1]
        """
        if not self.is_trained or not text:
            return None

        try:
            X = self.vectorizer.transform([text])
            prediction = self.classifier.predict(X)[0]
            probabilities = self.classifier.predict_proba(X)[0]

            # Convert probabilities to sentiment score (-1 to 1)
            # Assuming classes are [-1, 0, 1] in order
            sentiment_classes = sorted(self.classifier.classes_)
            score = sum(
                sent_class * prob
                for sent_class, prob in zip(sentiment_classes, probabilities)
            )

            result = {
                "sentiment": int(prediction),
                "score": round(float(score), 3),
                "label": self._sentiment_label(prediction),
                "confidence": round(float(max(probabilities)), 3),
            }
            return result

        except Exception as e:
            logger.error(f"Error analyzing sentiment with score: {e}")
            return None

    @staticmethod
    def _sentiment_label(sentiment: int) -> str:
        """Get human-readable sentiment label.

        Args:
            sentiment: Sentiment value (-1, 0, 1)

        Returns:
            Label string
        """
        labels = {-1: "negative", 0: "neutral", 1: "positive"}
        return labels.get(sentiment, "unknown")

    def is_negative(self, text: str, threshold: float = 0.5) -> bool:
        """Check if article has negative sentiment.

        Args:
            text: News text
            threshold: Confidence threshold

        Returns:
            True if article is likely negative
        """
        result = self.analyze_with_score(text)
        if not result:
            return False

        return result["sentiment"] == -1 and result["confidence"] >= threshold

    def is_positive(self, text: str, threshold: float = 0.5) -> bool:
        """Check if article has positive sentiment.

        Args:
            text: News text
            threshold: Confidence threshold

        Returns:
            True if article is likely positive
        """
        result = self.analyze_with_score(text)
        if not result:
            return False

        return result["sentiment"] == 1 and result["confidence"] >= threshold
