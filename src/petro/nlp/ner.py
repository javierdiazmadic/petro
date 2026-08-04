"""Named Entity Recognition for news articles."""

from typing import Dict, List, Optional

import spacy

from petro.core import get_logger

logger = get_logger(__name__)


class NamedEntityRecognizer:
    """Extracts named entities from news articles using spaCy."""

    # Entity types we care about
    ENTITY_TYPES = {
        "GPE": "country",  # Geopolitical entity (country)
        "ORG": "company",  # Organization
        "PERSON": "person",
        "PRODUCT": "product",
    }

    def __init__(self):
        """Initialize NER models."""
        self.models = {}
        self._load_models()

    def _load_models(self) -> None:
        """Load spaCy models for supported languages."""
        try:
            # Spanish model
            self.models["es"] = spacy.load("es_core_news_sm")
            logger.info("Loaded Spanish NER model")
        except OSError:
            logger.warning("Spanish NER model not found. Run: python -m spacy download es_core_news_sm")
            self.models["es"] = None

        try:
            # English model
            self.models["en"] = spacy.load("en_core_web_sm")
            logger.info("Loaded English NER model")
        except OSError:
            logger.warning("English NER model not found. Run: python -m spacy download en_core_web_sm")
            self.models["en"] = None

    def extract_entities(self, text: str, language: str = "es") -> Optional[Dict[str, List[str]]]:
        """Extract named entities from text.

        Args:
            text: Text to extract entities from
            language: Language code (es, en)

        Returns:
            Dictionary with entity types as keys and lists of entities as values
        """
        if not text or not self.models.get(language):
            return None

        try:
            nlp = self.models[language]
            doc = nlp(text)

            entities = {
                "countries": [],
                "companies": [],
                "people": [],
                "products": [],
            }

            for ent in doc.ents:
                if ent.label_ == "GPE" and ent.text not in entities["countries"]:
                    entities["countries"].append(ent.text)
                elif ent.label_ == "ORG" and ent.text not in entities["companies"]:
                    entities["companies"].append(ent.text)
                elif ent.label_ == "PERSON" and ent.text not in entities["people"]:
                    entities["people"].append(ent.text)
                elif ent.label_ == "PRODUCT" and ent.text not in entities["products"]:
                    entities["products"].append(ent.text)

            # Filter out empty lists
            return {k: v for k, v in entities.items() if v}

        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return None

    def extract_keywords(self, text: str, language: str = "es", top_n: int = 10) -> Optional[List[str]]:
        """Extract noun phrases as keywords from text.

        Args:
            text: Text to extract keywords from
            language: Language code
            top_n: Maximum number of keywords

        Returns:
            List of keywords (noun phrases)
        """
        if not text or not self.models.get(language):
            return None

        try:
            nlp = self.models[language]
            doc = nlp(text)

            # Extract noun chunks
            keywords = []
            for chunk in doc.noun_chunks:
                if chunk.text not in keywords and len(keywords) < top_n:
                    keywords.append(chunk.text)

            return keywords if keywords else None

        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return None
