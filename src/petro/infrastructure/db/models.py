"""SQLAlchemy ORM Models for Petro."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Price(Base):
    """Price data for gasolina 95 and gasóleo A in Spain.

    TimescaleDB hypertable on created_at.
    """

    __tablename__ = "price"
    __table_args__ = (Index("idx_price_created_at", "created_at", mysql_length=None),)

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, unique=True, index=True)
    price_gasolina_95 = Column(Float, nullable=False)
    price_gasoleoa = Column(Float, nullable=False)
    source = Column(String(100), nullable=False, default="geoportal")
    region = Column(String(100), nullable=True)  # Optional regional data
    meta_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<Price(timestamp={self.timestamp}, gasolina={self.price_gasolina_95}, gasoleoa={self.price_gasoleoa})>"


class IndicatorBrent(Base):
    """Brent crude oil prices (WTI equivalent).

    TimescaleDB hypertable on created_at.
    """

    __tablename__ = "indicator_brent"
    __table_args__ = (Index("idx_brent_created_at", "created_at", mysql_length=None),)

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, unique=True, index=True)
    value = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    unit = Column(String(20), nullable=False, default="barrel")
    source = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<IndicatorBrent(timestamp={self.timestamp}, value={self.value})>"


class IndicatorWTI(Base):
    """WTI crude oil prices.

    TimescaleDB hypertable on created_at.
    """

    __tablename__ = "indicator_wti"
    __table_args__ = (Index("idx_wti_created_at", "created_at", mysql_length=None),)

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, unique=True, index=True)
    value = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    unit = Column(String(20), nullable=False, default="barrel")
    source = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<IndicatorWTI(timestamp={self.timestamp}, value={self.value})>"


class IndicatorEURUSD(Base):
    """EUR/USD exchange rate.

    TimescaleDB hypertable on created_at.
    """

    __tablename__ = "indicator_eurusd"
    __table_args__ = (Index("idx_eurusd_created_at", "created_at", mysql_length=None),)

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, unique=True, index=True)
    value = Column(Float, nullable=False)
    source = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<IndicatorEURUSD(timestamp={self.timestamp}, value={self.value})>"


class InventoryEIA(Base):
    """EIA Inventory data (gasoline and distillates).

    TimescaleDB hypertable on created_at.
    """

    __tablename__ = "inventory_eia"
    __table_args__ = (Index("idx_inventory_created_at", "created_at", mysql_length=None),)

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    gasoline_inventory = Column(Float, nullable=True)
    distillate_inventory = Column(Float, nullable=True)
    crude_inventory = Column(Float, nullable=True)
    unit = Column(String(50), nullable=False, default="barrel")
    source = Column(String(100), nullable=False, default="eia")

    def __repr__(self):
        return f"<InventoryEIA(timestamp={self.timestamp})>"


class ProductionOPEC(Base):
    """OPEC production data.

    TimescaleDB hypertable on created_at.
    """

    __tablename__ = "production_opec"
    __table_args__ = (Index("idx_production_created_at", "created_at", mysql_length=None),)

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    total_production = Column(Float, nullable=True)
    unit = Column(String(50), nullable=False, default="barrel")
    source = Column(String(100), nullable=False, default="opec")
    meta_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<ProductionOPEC(timestamp={self.timestamp})>"


class News(Base):
    """Processed news data with metadata.

    TimescaleDB hypertable on created_at.
    """

    __tablename__ = "news"
    __table_args__ = (
        Index("idx_news_created_at", "created_at", mysql_length=None),
        Index("idx_news_language", "language"),
        Index("idx_news_classification", "classification"),
    )

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    published_at = Column(DateTime, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(200), nullable=False)
    source_url = Column(String(500), nullable=True)
    language = Column(String(10), nullable=False, default="es")
    classification = Column(String(100), nullable=True)  # Category of news
    entities = Column(JSON, nullable=True)  # {"countries": [...], "companies": [...], "refineries": [...]}
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    is_duplicate = Column(Integer, default=0)  # 1 if duplicate, 0 otherwise
    meta_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<News(id={self.id}, title={self.title[:50]}...)>"


class VariableEconomic(Base):
    """Economic variables derived from indicators.

    TimescaleDB hypertable on timestamp.
    """

    __tablename__ = "variable_economic"
    __table_args__ = (Index("idx_var_econ_timestamp", "timestamp", mysql_length=None),)

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    brent_change_1d = Column(Float, nullable=True)
    brent_change_7d = Column(Float, nullable=True)
    wti_change_1d = Column(Float, nullable=True)
    wti_change_7d = Column(Float, nullable=True)
    brent_wti_spread = Column(Float, nullable=True)
    eurusd_change_1d = Column(Float, nullable=True)
    eurusd_ratio = Column(Float, nullable=True)
    inventory_change_1w = Column(Float, nullable=True)
    production_change_1m = Column(Float, nullable=True)

    def __repr__(self):
        return f"<VariableEconomic(timestamp={self.timestamp})>"


class VariableTemporal(Base):
    """Temporal variables (day of week, hour, season, etc).

    TimescaleDB hypertable on timestamp.
    """

    __tablename__ = "variable_temporal"
    __table_args__ = (Index("idx_var_temporal_timestamp", "timestamp", mysql_length=None),)

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, unique=True, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0-6 (Monday-Sunday)
    day_of_month = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    is_weekend = Column(Integer, nullable=False)  # 1 or 0
    is_holiday = Column(Integer, nullable=False)  # 1 or 0
    season = Column(String(20), nullable=True)  # "spring", "summer", "autumn", "winter"
    days_since_last_opec = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<VariableTemporal(timestamp={self.timestamp})>"


class VariableStatistical(Base):
    """Statistical features (rolling averages, volatility, etc).

    TimescaleDB hypertable on timestamp.
    """

    __tablename__ = "variable_statistical"
    __table_args__ = (Index("idx_var_stat_timestamp", "timestamp", mysql_length=None),)

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    price_ma_7d = Column(Float, nullable=True)  # 7-day moving average
    price_ma_30d = Column(Float, nullable=True)  # 30-day moving average
    price_volatility_7d = Column(Float, nullable=True)  # Standard deviation
    price_volatility_30d = Column(Float, nullable=True)
    brent_ma_7d = Column(Float, nullable=True)
    brent_volatility_7d = Column(Float, nullable=True)
    price_lag_1d = Column(Float, nullable=True)  # Price from 1 day ago
    price_lag_7d = Column(Float, nullable=True)
    price_lag_30d = Column(Float, nullable=True)

    def __repr__(self):
        return f"<VariableStatistical(timestamp={self.timestamp})>"


class VariableTechnical(Base):
    """Technical indicators (RSI, MACD, Bollinger Bands, etc).

    TimescaleDB hypertable on timestamp.
    """

    __tablename__ = "variable_technical"
    __table_args__ = (Index("idx_var_tech_timestamp", "timestamp", mysql_length=None),)

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    rsi_14 = Column(Float, nullable=True)  # Relative Strength Index
    macd = Column(Float, nullable=True)  # MACD value
    macd_signal = Column(Float, nullable=True)
    macd_histogram = Column(Float, nullable=True)
    bb_upper = Column(Float, nullable=True)  # Bollinger Bands upper
    bb_middle = Column(Float, nullable=True)
    bb_lower = Column(Float, nullable=True)
    bb_width = Column(Float, nullable=True)
    bb_position = Column(Float, nullable=True)  # Position within bands [0, 1]

    def __repr__(self):
        return f"<VariableTechnical(timestamp={self.timestamp})>"


class VariableNews(Base):
    """Variables derived from news sentiment and frequency.

    TimescaleDB hypertable on timestamp.
    """

    __tablename__ = "variable_news"
    __table_args__ = (Index("idx_var_news_timestamp", "timestamp", mysql_length=None),)

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    news_count_1d = Column(Integer, nullable=True)  # Number of news in last 24h
    news_count_7d = Column(Integer, nullable=True)
    avg_sentiment_1d = Column(Float, nullable=True)  # Average sentiment score
    avg_sentiment_7d = Column(Float, nullable=True)
    positive_news_1d = Column(Integer, nullable=True)
    negative_news_1d = Column(Integer, nullable=True)
    news_about_opec = Column(Integer, nullable=True)
    news_about_production = Column(Integer, nullable=True)
    news_about_refinery = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<VariableNews(timestamp={self.timestamp})>"


class Forecast(Base):
    """Model predictions and forecasts.

    TimescaleDB hypertable on created_at.
    """

    __tablename__ = "forecast"
    __table_args__ = (
        Index("idx_forecast_created_at", "created_at", mysql_length=None),
        Index("idx_forecast_horizon", "horizon_days"),
        Index("idx_forecast_model", "model_version"),
    )

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)  # When the prediction was made
    commodity = Column(String(20), nullable=False)  # "gasolina_95" or "gasoleoa"
    predicted_price = Column(Float, nullable=False)  # Regression output
    direction = Column(String(10), nullable=False)  # "up", "down", "stable"
    direction_probability = Column(Float, nullable=False)  # [0, 1]
    horizon_days = Column(Integer, nullable=False)  # 1, 7, 30, etc
    model_version = Column(String(100), nullable=False)
    confidence_lower = Column(Float, nullable=True)  # Lower confidence interval
    confidence_upper = Column(Float, nullable=True)  # Upper confidence interval
    actual_price = Column(Float, nullable=True)  # Filled in later when price is known
    error = Column(Float, nullable=True)  # |predicted - actual|

    # Relationship to explanations
    explanations = relationship("Explanation", back_populates="forecast", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Forecast(id={self.id}, commodity={self.commodity}, predicted={self.predicted_price})>"


class Explanation(Base):
    """SHAP-based explanations for individual forecasts."""

    __tablename__ = "explanation"
    __table_args__ = (Index("idx_explanation_forecast_id", "forecast_id"),)

    id = Column(Integer, primary_key=True, index=True)
    forecast_id = Column(Integer, ForeignKey("forecast.id"), nullable=False, index=True)
    factor_name = Column(String(100), nullable=False)  # Variable name (e.g., "brent_change_1d")
    contribution_shap = Column(Float, nullable=False)  # SHAP value
    contribution_rank = Column(Integer, nullable=True)  # Rank of importance (1st, 2nd, etc)
    explanation_text = Column(Text, nullable=True)  # Human-readable explanation

    # Relationship to forecast
    forecast = relationship("Forecast", back_populates="explanations")

    def __repr__(self):
        return f"<Explanation(forecast_id={self.forecast_id}, factor={self.factor_name})>"


class ModelRegistry(Base):
    """Track different versions of trained models."""

    __tablename__ = "model_registry"
    __table_args__ = (Index("idx_model_status", "status"),)

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    model_type = Column(String(50), nullable=False)  # "xgboost", "lightgbm", "rf"
    commodity = Column(String(20), nullable=False)  # "gasolina_95", "gasoleoa", "all"
    status = Column(String(20), nullable=False, default="training")  # "training", "production", "archived"
    rmse_train = Column(Float, nullable=True)
    rmse_test = Column(Float, nullable=True)
    mae_train = Column(Float, nullable=True)
    mae_test = Column(Float, nullable=True)
    mape_test = Column(Float, nullable=True)
    r2_test = Column(Float, nullable=True)
    model_path = Column(String(500), nullable=False)  # Path to .pkl file
    scaler_path = Column(String(500), nullable=True)  # Path to scaler
    hyperparameters = Column(JSON, nullable=True)  # Model hyperparams
    feature_names = Column(JSON, nullable=True)  # List of feature names used
    mlflow_run_id = Column(String(100), nullable=True)  # MLflow tracking ID
    mlflow_experiment_id = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ModelRegistry(id={self.id}, model={self.model_type}, status={self.status})>"


class SystemLog(Base):
    """System-level logs for important business events.

    TimescaleDB hypertable on created_at.
    """

    __tablename__ = "system_log"
    __table_args__ = (
        Index("idx_log_created_at", "created_at", mysql_length=None),
        Index("idx_log_level", "level"),
        Index("idx_log_component", "component"),
    )

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(String(20), nullable=False)  # "info", "warning", "error", "critical"
    component = Column(String(100), nullable=False)  # e.g., "ingestion", "training", "inference"
    message = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)  # Additional context data

    def __repr__(self):
        return f"<SystemLog(level={self.level}, component={self.component}, message={self.message[:50]}...)>"
