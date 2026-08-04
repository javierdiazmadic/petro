"""Create initial database schema.

Revision ID: 001
Revises:
Create Date: 2026-08-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables."""

    # Enable TimescaleDB extension
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")

    # Price table (hypertable)
    op.create_table(
        "price",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("price_gasolina_95", sa.Float(), nullable=False),
        sa.Column("price_gasoleoa", sa.Float(), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("timestamp"),
    )
    op.create_index("idx_price_created_at", "price", ["created_at"])
    op.execute("SELECT create_hypertable('price', 'created_at', if_not_exists => TRUE)")

    # Indicator Brent (hypertable)
    op.create_table(
        "indicator_brent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("timestamp"),
    )
    op.create_index("idx_brent_created_at", "indicator_brent", ["created_at"])
    op.execute(
        "SELECT create_hypertable('indicator_brent', 'created_at', if_not_exists => TRUE)"
    )

    # Indicator WTI (hypertable)
    op.create_table(
        "indicator_wti",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("timestamp"),
    )
    op.create_index("idx_wti_created_at", "indicator_wti", ["created_at"])
    op.execute(
        "SELECT create_hypertable('indicator_wti', 'created_at', if_not_exists => TRUE)"
    )

    # Indicator EUR/USD (hypertable)
    op.create_table(
        "indicator_eurusd",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("timestamp"),
    )
    op.create_index("idx_eurusd_created_at", "indicator_eurusd", ["created_at"])
    op.execute(
        "SELECT create_hypertable('indicator_eurusd', 'created_at', if_not_exists => TRUE)"
    )

    # Inventory EIA (hypertable)
    op.create_table(
        "inventory_eia",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("gasoline_inventory", sa.Float(), nullable=True),
        sa.Column("distillate_inventory", sa.Float(), nullable=True),
        sa.Column("crude_inventory", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_inventory_created_at", "inventory_eia", ["created_at"])
    op.execute(
        "SELECT create_hypertable('inventory_eia', 'created_at', if_not_exists => TRUE)"
    )

    # Production OPEC (hypertable)
    op.create_table(
        "production_opec",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("total_production", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_production_created_at", "production_opec", ["created_at"])
    op.execute(
        "SELECT create_hypertable('production_opec', 'created_at', if_not_exists => TRUE)"
    )

    # News (hypertable)
    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(200), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("language", sa.String(10), nullable=False),
        sa.Column("classification", sa.String(100), nullable=True),
        sa.Column("entities", sa.JSON(), nullable=True),
        sa.Column("sentiment_score", sa.Float(), nullable=True),
        sa.Column("is_duplicate", sa.Integer(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_news_created_at", "news", ["created_at"])
    op.create_index("idx_news_language", "news", ["language"])
    op.create_index("idx_news_classification", "news", ["classification"])
    op.execute("SELECT create_hypertable('news', 'created_at', if_not_exists => TRUE)")

    # Variable Economic (hypertable)
    op.create_table(
        "variable_economic",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("brent_change_1d", sa.Float(), nullable=True),
        sa.Column("brent_change_7d", sa.Float(), nullable=True),
        sa.Column("wti_change_1d", sa.Float(), nullable=True),
        sa.Column("wti_change_7d", sa.Float(), nullable=True),
        sa.Column("brent_wti_spread", sa.Float(), nullable=True),
        sa.Column("eurusd_change_1d", sa.Float(), nullable=True),
        sa.Column("eurusd_ratio", sa.Float(), nullable=True),
        sa.Column("inventory_change_1w", sa.Float(), nullable=True),
        sa.Column("production_change_1m", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_var_econ_timestamp", "variable_economic", ["timestamp"])
    op.execute(
        "SELECT create_hypertable('variable_economic', 'timestamp', if_not_exists => TRUE)"
    )

    # Variable Temporal (hypertable)
    op.create_table(
        "variable_temporal",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("day_of_month", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("quarter", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("hour", sa.Integer(), nullable=False),
        sa.Column("is_weekend", sa.Integer(), nullable=False),
        sa.Column("is_holiday", sa.Integer(), nullable=False),
        sa.Column("season", sa.String(20), nullable=True),
        sa.Column("days_since_last_opec", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("timestamp"),
    )
    op.create_index("idx_var_temporal_timestamp", "variable_temporal", ["timestamp"])
    op.execute(
        "SELECT create_hypertable('variable_temporal', 'timestamp', if_not_exists => TRUE)"
    )

    # Variable Statistical (hypertable)
    op.create_table(
        "variable_statistical",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("price_ma_7d", sa.Float(), nullable=True),
        sa.Column("price_ma_30d", sa.Float(), nullable=True),
        sa.Column("price_volatility_7d", sa.Float(), nullable=True),
        sa.Column("price_volatility_30d", sa.Float(), nullable=True),
        sa.Column("brent_ma_7d", sa.Float(), nullable=True),
        sa.Column("brent_volatility_7d", sa.Float(), nullable=True),
        sa.Column("price_lag_1d", sa.Float(), nullable=True),
        sa.Column("price_lag_7d", sa.Float(), nullable=True),
        sa.Column("price_lag_30d", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_var_stat_timestamp", "variable_statistical", ["timestamp"])
    op.execute(
        "SELECT create_hypertable('variable_statistical', 'timestamp', if_not_exists => TRUE)"
    )

    # Variable Technical (hypertable)
    op.create_table(
        "variable_technical",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("rsi_14", sa.Float(), nullable=True),
        sa.Column("macd", sa.Float(), nullable=True),
        sa.Column("macd_signal", sa.Float(), nullable=True),
        sa.Column("macd_histogram", sa.Float(), nullable=True),
        sa.Column("bb_upper", sa.Float(), nullable=True),
        sa.Column("bb_middle", sa.Float(), nullable=True),
        sa.Column("bb_lower", sa.Float(), nullable=True),
        sa.Column("bb_width", sa.Float(), nullable=True),
        sa.Column("bb_position", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_var_tech_timestamp", "variable_technical", ["timestamp"])
    op.execute(
        "SELECT create_hypertable('variable_technical', 'timestamp', if_not_exists => TRUE)"
    )

    # Variable News (hypertable)
    op.create_table(
        "variable_news",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("news_count_1d", sa.Integer(), nullable=True),
        sa.Column("news_count_7d", sa.Integer(), nullable=True),
        sa.Column("avg_sentiment_1d", sa.Float(), nullable=True),
        sa.Column("avg_sentiment_7d", sa.Float(), nullable=True),
        sa.Column("positive_news_1d", sa.Integer(), nullable=True),
        sa.Column("negative_news_1d", sa.Integer(), nullable=True),
        sa.Column("news_about_opec", sa.Integer(), nullable=True),
        sa.Column("news_about_production", sa.Integer(), nullable=True),
        sa.Column("news_about_refinery", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_var_news_timestamp", "variable_news", ["timestamp"])
    op.execute(
        "SELECT create_hypertable('variable_news', 'timestamp', if_not_exists => TRUE)"
    )

    # Forecast (hypertable)
    op.create_table(
        "forecast",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("commodity", sa.String(20), nullable=False),
        sa.Column("predicted_price", sa.Float(), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("direction_probability", sa.Float(), nullable=False),
        sa.Column("horizon_days", sa.Integer(), nullable=False),
        sa.Column("model_version", sa.String(100), nullable=False),
        sa.Column("confidence_lower", sa.Float(), nullable=True),
        sa.Column("confidence_upper", sa.Float(), nullable=True),
        sa.Column("actual_price", sa.Float(), nullable=True),
        sa.Column("error", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_forecast_created_at", "forecast", ["created_at"])
    op.create_index("idx_forecast_horizon", "forecast", ["horizon_days"])
    op.create_index("idx_forecast_model", "forecast", ["model_version"])
    op.execute("SELECT create_hypertable('forecast', 'created_at', if_not_exists => TRUE)")

    # Explanation (regular table, not hypertable)
    op.create_table(
        "explanation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("forecast_id", sa.Integer(), nullable=False),
        sa.Column("factor_name", sa.String(100), nullable=False),
        sa.Column("contribution_shap", sa.Float(), nullable=False),
        sa.Column("contribution_rank", sa.Integer(), nullable=True),
        sa.Column("explanation_text", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["forecast_id"], ["forecast.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_explanation_forecast_id", "explanation", ["forecast_id"])

    # Model Registry (regular table)
    op.create_table(
        "model_registry",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("model_type", sa.String(50), nullable=False),
        sa.Column("commodity", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("rmse_train", sa.Float(), nullable=True),
        sa.Column("rmse_test", sa.Float(), nullable=True),
        sa.Column("mae_train", sa.Float(), nullable=True),
        sa.Column("mae_test", sa.Float(), nullable=True),
        sa.Column("mape_test", sa.Float(), nullable=True),
        sa.Column("r2_test", sa.Float(), nullable=True),
        sa.Column("model_path", sa.String(500), nullable=False),
        sa.Column("scaler_path", sa.String(500), nullable=True),
        sa.Column("hyperparameters", sa.JSON(), nullable=True),
        sa.Column("feature_names", sa.JSON(), nullable=True),
        sa.Column("mlflow_run_id", sa.String(100), nullable=True),
        sa.Column("mlflow_experiment_id", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_model_status", "model_registry", ["status"])

    # System Log (hypertable)
    op.create_table(
        "system_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("component", sa.String(100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_log_created_at", "system_log", ["created_at"])
    op.create_index("idx_log_level", "system_log", ["level"])
    op.create_index("idx_log_component", "system_log", ["component"])
    op.execute(
        "SELECT create_hypertable('system_log', 'created_at', if_not_exists => TRUE)"
    )


def downgrade() -> None:
    """Drop all tables."""

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table("system_log")
    op.drop_table("model_registry")
    op.drop_table("explanation")
    op.drop_table("forecast")
    op.drop_table("variable_news")
    op.drop_table("variable_technical")
    op.drop_table("variable_statistical")
    op.drop_table("variable_temporal")
    op.drop_table("variable_economic")
    op.drop_table("news")
    op.drop_table("production_opec")
    op.drop_table("inventory_eia")
    op.drop_table("indicator_eurusd")
    op.drop_table("indicator_wti")
    op.drop_table("indicator_brent")
    op.drop_table("price")
