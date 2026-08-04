"""Features derived from news articles."""

from typing import List, Optional


class NewsDerivedFeatures:
    """Calculate features based on news sentiment and frequency."""

    @staticmethod
    def news_count_metrics(
        articles_1d: Optional[List[dict]] = None,
        articles_7d: Optional[List[dict]] = None,
    ) -> dict:
        """Calculate news frequency metrics.

        Args:
            articles_1d: News articles from last 24 hours
            articles_7d: News articles from last 7 days

        Returns:
            Dictionary with news count metrics
        """
        count_1d = len(articles_1d) if articles_1d else 0
        count_7d = len(articles_7d) if articles_7d else 0

        # Average articles per day
        avg_per_day = count_7d / 7 if count_7d > 0 else 0

        return {
            "news_count_1d": count_1d,
            "news_count_7d": count_7d,
            "news_avg_per_day_7d": round(avg_per_day, 2),
        }

    @staticmethod
    def sentiment_metrics(
        articles_1d: Optional[List[dict]] = None,
        articles_7d: Optional[List[dict]] = None,
    ) -> dict:
        """Calculate sentiment metrics from news.

        Args:
            articles_1d: News articles from last 24 hours (with sentiment_score)
            articles_7d: News articles from last 7 days

        Returns:
            Dictionary with sentiment metrics
        """
        def get_avg_sentiment(articles):
            if not articles:
                return None
            sentiments = [
                a.get("sentiment_score")
                for a in articles
                if a.get("sentiment_score") is not None
            ]
            if not sentiments:
                return None
            return sum(sentiments) / len(sentiments)

        avg_sentiment_1d = get_avg_sentiment(articles_1d)
        avg_sentiment_7d = get_avg_sentiment(articles_7d)

        return {
            "avg_sentiment_1d": round(avg_sentiment_1d, 3) if avg_sentiment_1d else None,
            "avg_sentiment_7d": round(avg_sentiment_7d, 3) if avg_sentiment_7d else None,
        }

    @staticmethod
    def sentiment_distribution(
        articles: Optional[List[dict]] = None,
    ) -> dict:
        """Calculate distribution of sentiment (positive/negative/neutral).

        Args:
            articles: News articles (with sentiment_score)

        Returns:
            Dictionary with sentiment counts
        """
        if not articles:
            return {
                "positive_news_count": 0,
                "negative_news_count": 0,
                "neutral_news_count": 0,
            }

        positive = sum(1 for a in articles if a.get("sentiment_score", 0) > 0.3)
        negative = sum(1 for a in articles if a.get("sentiment_score", 0) < -0.3)
        neutral = len(articles) - positive - negative

        return {
            "positive_news_count": positive,
            "negative_news_count": negative,
            "neutral_news_count": neutral,
        }

    @staticmethod
    def topic_frequency(
        articles: Optional[List[dict]] = None,
    ) -> dict:
        """Calculate frequency of news topics.

        Args:
            articles: News articles (with classification)

        Returns:
            Dictionary with topic counts
        """
        if not articles:
            return {
                "news_about_opec": 0,
                "news_about_production": 0,
                "news_about_refinery": 0,
                "news_about_geopolitics": 0,
                "news_about_supply": 0,
                "news_about_demand": 0,
            }

        classifications = [a.get("classification", "other") for a in articles]

        return {
            "news_about_opec": classifications.count("opec"),
            "news_about_production": classifications.count("production"),
            "news_about_refinery": classifications.count("refinery"),
            "news_about_geopolitics": classifications.count("geopolitics"),
            "news_about_supply": classifications.count("supply"),
            "news_about_demand": classifications.count("demand"),
        }

    @staticmethod
    def entity_frequency(
        articles: Optional[List[dict]] = None,
    ) -> dict:
        """Calculate frequency of entity mentions in news.

        Args:
            articles: News articles (with entities)

        Returns:
            Dictionary with entity mention counts
        """
        if not articles:
            return {
                "countries_mentioned": 0,
                "companies_mentioned": 0,
                "unique_countries": 0,
                "unique_companies": 0,
            }

        countries = set()
        companies = set()
        country_count = 0
        company_count = 0

        for article in articles:
            entities = article.get("entities", {})

            if entities.get("countries"):
                country_list = entities["countries"]
                country_count += len(country_list)
                countries.update(country_list)

            if entities.get("companies"):
                company_list = entities["companies"]
                company_count += len(company_list)
                companies.update(company_list)

        return {
            "countries_mentioned": country_count,
            "companies_mentioned": company_count,
            "unique_countries": len(countries),
            "unique_companies": len(companies),
        }

    @staticmethod
    def news_momentum(
        articles_current: Optional[List[dict]] = None,
        articles_previous: Optional[List[dict]] = None,
    ) -> Optional[float]:
        """Calculate momentum in news volume/sentiment.

        Args:
            articles_current: Recent articles
            articles_previous: Previous period articles

        Returns:
            Momentum score or None
        """
        current_count = len(articles_current) if articles_current else 0
        previous_count = len(articles_previous) if articles_previous else 0

        if previous_count == 0:
            return None

        momentum = ((current_count - previous_count) / previous_count) * 100
        return round(momentum, 2)
