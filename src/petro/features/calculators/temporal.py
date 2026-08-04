"""Temporal feature calculations."""

from datetime import datetime
from typing import Optional


class TemporalFeatures:
    """Calculate time-based features."""

    # Holiday dates (Spain)
    SPANISH_HOLIDAYS = [
        "01-01",  # New Year
        "01-06",  # Epiphany
        "05-01",  # Labour Day
        "08-15",  # Assumption
        "10-12",  # National Day
        "11-01",  # All Saints
        "12-25",  # Christmas
    ]

    # Seasons (Northern Hemisphere)
    SEASONS = {
        (12, 1, 2): "winter",
        (3, 4, 5): "spring",
        (6, 7, 8): "summer",
        (9, 10, 11): "autumn",
    }

    @staticmethod
    def extract_temporal_features(timestamp: datetime) -> dict:
        """Extract all temporal features from timestamp.

        Args:
            timestamp: Datetime to extract from

        Returns:
            Dictionary with temporal features
        """
        day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
        day_of_month = timestamp.day
        month = timestamp.month
        year = timestamp.year
        hour = timestamp.hour
        quarter = (month - 1) // 3 + 1

        # Season
        season = None
        for months, season_name in TemporalFeatures.SEASONS.items():
            if month in months:
                season = season_name
                break

        # Weekend
        is_weekend = 1 if day_of_week >= 5 else 0

        # Holiday (Spanish holidays)
        is_holiday = 1 if f"{month:02d}-{day_of_month:02d}" in TemporalFeatures.SPANISH_HOLIDAYS else 0

        return {
            "day_of_week": day_of_week,
            "day_of_month": day_of_month,
            "month": month,
            "quarter": quarter,
            "year": year,
            "hour": hour,
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
            "season": season,
            "week_of_year": timestamp.isocalendar()[1],
        }

    @staticmethod
    def days_since_last_event(
        current_timestamp: datetime, last_event_timestamp: Optional[datetime]
    ) -> Optional[int]:
        """Calculate days since last event (e.g., OPEC announcement).

        Args:
            current_timestamp: Current datetime
            last_event_timestamp: Last event datetime

        Returns:
            Days since event, or None if no event
        """
        if not last_event_timestamp:
            return None

        delta = current_timestamp - last_event_timestamp
        return delta.days

    @staticmethod
    def is_trading_hours(timestamp: datetime) -> int:
        """Check if timestamp is during trading hours (9 AM - 5 PM, weekdays).

        Args:
            timestamp: Datetime to check

        Returns:
            1 if trading hours, 0 otherwise
        """
        is_weekday = timestamp.weekday() < 5
        is_trading_time = 9 <= timestamp.hour < 17

        return 1 if (is_weekday and is_trading_time) else 0

    @staticmethod
    def time_to_event(
        current_timestamp: datetime, event_timestamp: datetime
    ) -> Optional[int]:
        """Calculate hours until next event.

        Args:
            current_timestamp: Current datetime
            event_timestamp: Event datetime

        Returns:
            Hours until event, or None if past
        """
        if event_timestamp <= current_timestamp:
            return None

        delta = event_timestamp - current_timestamp
        return int(delta.total_seconds() / 3600)
