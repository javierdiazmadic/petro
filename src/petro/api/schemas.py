"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ===== Prediction Schemas =====

class ConfidenceScores(BaseModel):
    """Price direction confidence scores."""

    up: float = Field(..., ge=0, le=1, description="Probability of price increase")
    stable: float = Field(..., ge=0, le=1, description="Probability of stable price")
    down: float = Field(..., ge=0, le=1, description="Probability of price decrease")

    class Config:
        json_schema_extra = {
            "example": {
                "up": 0.75,
                "stable": 0.15,
                "down": 0.10,
            }
        }


class ConfidenceBounds(BaseModel):
    """Confidence interval bounds for prediction."""

    lower: float = Field(..., description="Lower bound (pessimistic scenario)")
    upper: float = Field(..., description="Upper bound (optimistic scenario)")
    uncertainty_pct: float = Field(..., description="Uncertainty margin percentage")

    class Config:
        json_schema_extra = {
            "example": {
                "lower": 1.447,
                "upper": 1.599,
                "uncertainty_pct": 5.0,
            }
        }


class PricePredictor(BaseModel):
    """Single price prediction for a horizon."""

    timestamp: datetime = Field(..., description="Prediction timestamp (UTC)")
    horizon: str = Field(..., description="Prediction horizon (e.g., '1d', '3d', '7d')")
    product: str = Field(..., description="Fuel product (gasolina_95 or gasóleo_a)")
    current_price: float = Field(..., gt=0, description="Current price (€/L)")
    predicted_price: float = Field(..., gt=0, description="Predicted price (€/L)")
    change: float = Field(..., description="Absolute price change (€/L)")
    change_pct: float = Field(..., description="Percentage price change (%)")
    direction: str = Field(..., description="Direction classification (up, down, stable)")
    confidence: ConfidenceScores = Field(..., description="Direction confidence scores")
    bounds: ConfidenceBounds = Field(..., description="Confidence interval bounds")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-08-04T15:30:00Z",
                "horizon": "1d",
                "product": "gasolina_95",
                "current_price": 1.50,
                "predicted_price": 1.523,
                "change": 0.023,
                "change_pct": 1.53,
                "direction": "up",
                "confidence": {
                    "up": 0.79,
                    "stable": 0.15,
                    "down": 0.06,
                },
                "bounds": {
                    "lower": 1.447,
                    "upper": 1.599,
                    "uncertainty_pct": 5.0,
                },
            }
        }


class ForecastResponse(BaseModel):
    """Multi-horizon forecast response."""

    timestamp: datetime = Field(..., description="Forecast generation timestamp")
    forecast_valid_until: datetime = Field(..., description="Forecast validity period end")
    predictions: Dict[str, List[PricePredictor]] = Field(
        ..., description="Predictions by product and horizon"
    )
    model_info: Optional[Dict] = Field(
        None, description="Information about trained model"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-08-04T15:30:00Z",
                "forecast_valid_until": "2026-08-04T15:45:00Z",
                "predictions": {
                    "gasolina_95": [
                        {
                            "timestamp": "2026-08-04T15:30:00Z",
                            "horizon": "1d",
                            "product": "gasolina_95",
                            "current_price": 1.50,
                            "predicted_price": 1.523,
                            "change": 0.023,
                            "change_pct": 1.53,
                            "direction": "up",
                            "confidence": {"up": 0.79, "stable": 0.15, "down": 0.06},
                            "bounds": {
                                "lower": 1.447,
                                "upper": 1.599,
                                "uncertainty_pct": 5.0,
                            },
                        }
                    ],
                    "gasóleo_a": [
                        {
                            "timestamp": "2026-08-04T15:30:00Z",
                            "horizon": "1d",
                            "product": "gasóleo_a",
                            "current_price": 1.35,
                            "predicted_price": 1.372,
                            "change": 0.022,
                            "change_pct": 1.63,
                            "direction": "up",
                            "confidence": {"up": 0.76, "stable": 0.18, "down": 0.06},
                            "bounds": {
                                "lower": 1.304,
                                "upper": 1.440,
                                "uncertainty_pct": 5.0,
                            },
                        }
                    ],
                },
                "model_info": {
                    "run_id": "abc-123-def-456",
                    "rmse": 0.0523,
                    "r2": 0.8645,
                },
            }
        }


# ===== Metrics Schemas =====

class ModelMetrics(BaseModel):
    """Model performance metrics."""

    rmse: float = Field(..., description="Root Mean Squared Error")
    mae: float = Field(..., description="Mean Absolute Error")
    r2: float = Field(..., ge=-1, le=1, description="R-squared (coefficient of determination)")
    mape: float = Field(..., ge=0, description="Mean Absolute Percentage Error (%)")

    class Config:
        json_schema_extra = {
            "example": {
                "rmse": 0.0523,
                "mae": 0.0412,
                "r2": 0.8645,
                "mape": 2.75,
            }
        }


class ModelComparison(BaseModel):
    """Comparison of multiple trained models."""

    best_model: str = Field(..., description="Best model type (xgboost, lightgbm, random_forest)")
    best_metrics: ModelMetrics = Field(..., description="Metrics of best model")
    all_models: Dict[str, ModelMetrics] = Field(
        ..., description="Metrics for all trained models"
    )
    last_training: datetime = Field(..., description="Last model training timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "best_model": "xgboost",
                "best_metrics": {
                    "rmse": 0.0523,
                    "mae": 0.0412,
                    "r2": 0.8645,
                    "mape": 2.75,
                },
                "all_models": {
                    "xgboost": {
                        "rmse": 0.0523,
                        "mae": 0.0412,
                        "r2": 0.8645,
                        "mape": 2.75,
                    },
                    "lightgbm": {
                        "rmse": 0.0598,
                        "mae": 0.0467,
                        "r2": 0.8412,
                        "mape": 3.12,
                    },
                },
                "last_training": "2026-08-04T02:00:00Z",
            }
        }


class HistoricalPrediction(BaseModel):
    """Historical prediction record."""

    timestamp: datetime = Field(..., description="Prediction generation time")
    actual_price: Optional[float] = Field(None, description="Actual price (if available)")
    predicted_price: float = Field(..., description="Predicted price")
    error: Optional[float] = Field(None, description="Actual - Predicted (if available)")
    direction: str = Field(..., description="Predicted direction")
    confidence: ConfidenceScores = Field(..., description="Confidence scores")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-08-04T15:30:00Z",
                "actual_price": 1.525,
                "predicted_price": 1.523,
                "error": 0.002,
                "direction": "up",
                "confidence": {"up": 0.79, "stable": 0.15, "down": 0.06},
            }
        }


class HistoryResponse(BaseModel):
    """Historical predictions response."""

    product: str = Field(..., description="Fuel product")
    horizon: str = Field(..., description="Prediction horizon")
    count: int = Field(..., ge=0, description="Number of predictions returned")
    total_count: int = Field(..., ge=0, description="Total predictions available")
    predictions: List[HistoricalPrediction] = Field(..., description="Historical predictions")
    accuracy_metrics: Optional[Dict[str, float]] = Field(
        None, description="Accuracy metrics (MAE, RMSE, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product": "gasolina_95",
                "horizon": "1d",
                "count": 10,
                "total_count": 450,
                "predictions": [
                    {
                        "timestamp": "2026-08-04T15:30:00Z",
                        "actual_price": 1.525,
                        "predicted_price": 1.523,
                        "error": 0.002,
                        "direction": "up",
                        "confidence": {"up": 0.79, "stable": 0.15, "down": 0.06},
                    }
                ],
                "accuracy_metrics": {
                    "mae": 0.0412,
                    "rmse": 0.0523,
                    "mape": 2.75,
                },
            }
        }


# ===== Feature Importance Schemas =====

class FeatureImportance(BaseModel):
    """Feature importance for model interpretability."""

    feature_name: str = Field(..., description="Name of the feature")
    importance: float = Field(..., ge=0, description="Importance score")
    rank: int = Field(..., ge=1, description="Feature ranking (1=most important)")

    class Config:
        json_schema_extra = {
            "example": {
                "feature_name": "price_momentum_10d",
                "importance": 0.245,
                "rank": 1,
            }
        }


class ExplainabilityResponse(BaseModel):
    """Model explainability information."""

    model_type: str = Field(..., description="Type of model (xgboost, lightgbm, etc.)")
    feature_importance: List[FeatureImportance] = Field(
        ..., description="Top features and their importance scores"
    )
    timestamp: datetime = Field(..., description="Explanation generation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "model_type": "xgboost",
                "feature_importance": [
                    {
                        "feature_name": "price_momentum_10d",
                        "importance": 0.245,
                        "rank": 1,
                    },
                    {
                        "feature_name": "brent_price",
                        "importance": 0.198,
                        "rank": 2,
                    },
                ],
                "timestamp": "2026-08-04T15:30:00Z",
            }
        }


# ===== Health & Status Schemas =====

class HealthStatus(BaseModel):
    """System health status."""

    status: str = Field(..., description="Overall status (healthy, degraded, unhealthy)")
    timestamp: datetime = Field(..., description="Health check timestamp")
    database: str = Field(..., description="Database connection status")
    redis: str = Field(..., description="Redis connection status")
    model_loaded: bool = Field(..., description="Is ML model loaded")
    last_cycle: Optional[datetime] = Field(None, description="Last pipeline cycle completion")
    version: str = Field(..., description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-08-04T15:30:00Z",
                "database": "connected",
                "redis": "connected",
                "model_loaded": True,
                "last_cycle": "2026-08-04T15:30:00Z",
                "version": "0.9.0",
            }
        }


# ===== Error Schemas =====

class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for programmatic handling")
    timestamp: datetime = Field(..., description="Error timestamp")
    details: Optional[Dict] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Model not loaded. Pipeline may not have completed.",
                "error_code": "MODEL_NOT_AVAILABLE",
                "timestamp": "2026-08-04T15:30:00Z",
                "details": {
                    "last_attempt": "2026-08-04T15:15:00Z",
                    "retry_in_seconds": 300,
                },
            }
        }


# ===== Request Query Schemas =====

class PredictQuery(BaseModel):
    """Query parameters for predict endpoint."""

    product: str = Field(default="gasolina_95", description="Fuel product")
    horizons: Optional[str] = Field(
        default="1d,3d,7d", description="Comma-separated horizons (1d, 3d, 7d)"
    )
    include_bounds: bool = Field(default=True, description="Include confidence bounds")

    class Config:
        json_schema_extra = {
            "example": {
                "product": "gasolina_95",
                "horizons": "1d,3d,7d",
                "include_bounds": True,
            }
        }


class HistoryQuery(BaseModel):
    """Query parameters for history endpoint."""

    product: str = Field(default="gasolina_95", description="Fuel product")
    horizon: str = Field(default="1d", description="Prediction horizon")
    days: int = Field(default=30, ge=1, le=365, description="Number of days of history")
    include_accuracy: bool = Field(default=True, description="Include accuracy metrics")

    class Config:
        json_schema_extra = {
            "example": {
                "product": "gasolina_95",
                "horizon": "1d",
                "days": 30,
                "include_accuracy": True,
            }
        }
