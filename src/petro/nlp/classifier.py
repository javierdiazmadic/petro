"""News classification using TF-IDF and Logistic Regression."""

from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from petro.core import get_logger

logger = get_logger(__name__)


class NewsClassifier:
    """Classifies news articles into categories using TF-IDF + LogisticRegression."""

    # News categories relevant to fuel prices
    CATEGORIES = [
        "opec",  # OPEC announcements/production
        "refinery",  # Refinery issues/shutdowns
        "geopolitics",  # Geopolitical events
        "supply",  # Supply issues
        "demand",  # Demand related
        "other",  # Other
    ]

    def __init__(self):
        """Initialize classifier."""
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2),
            lowercase=True,
            stop_words="english",
        )
        self.classifier = LogisticRegression(max_iter=1000, random_state=42)
        self.is_trained = False

    def train(self, texts: list, labels: list) -> bool:
        """Train classifier on labeled examples.

        Args:
            texts: List of news texts
            labels: List of category labels (must match CATEGORIES)

        Returns:
            True if training successful
        """
        if len(texts) != len(labels):
            logger.error("Number of texts must match number of labels")
            return False

        # Validate labels
        for label in labels:
            if label not in self.CATEGORIES:
                logger.error(f"Invalid label: {label}")
                return False

        try:
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, labels)
            self.is_trained = True
            logger.info(f"Classifier trained on {len(texts)} examples")
            return True

        except Exception as e:
            logger.error(f"Error training classifier: {e}")
            return False

    def classify(self, text: str) -> Optional[str]:
        """Classify a news article.

        Args:
            text: News text to classify

        Returns:
            Category label or None if not trained
        """
        if not self.is_trained or not text:
            return None

        try:
            X = self.vectorizer.transform([text])
            prediction = self.classifier.predict(X)[0]
            return prediction

        except Exception as e:
            logger.error(f"Error classifying text: {e}")
            return None

    def classify_with_confidence(self, text: str) -> Optional[dict]:
        """Classify with confidence scores.

        Args:
            text: News text to classify

        Returns:
            Dictionary with category, confidence, and all probabilities
        """
        if not self.is_trained or not text:
            return None

        try:
            X = self.vectorizer.transform([text])
            prediction = self.classifier.predict(X)[0]
            probabilities = self.classifier.predict_proba(X)[0]

            result = {
                "category": prediction,
                "confidence": float(max(probabilities)),
                "probabilities": {
                    cat: round(float(prob), 3)
                    for cat, prob in zip(self.CATEGORIES, probabilities)
                },
            }
            return result

        except Exception as e:
            logger.error(f"Error classifying with confidence: {e}")
            return None

    def is_relevant(self, text: str, threshold: float = 0.5) -> bool:
        """Check if article is relevant to fuel prices.

        Args:
            text: News text
            threshold: Confidence threshold

        Returns:
            True if article is likely relevant
        """
        result = self.classify_with_confidence(text)
        if not result:
            return False

        # Check if highest confidence category is not "other"
        if result["category"] == "other":
            return result["confidence"] < (1 - threshold)

        return result["confidence"] >= threshold
