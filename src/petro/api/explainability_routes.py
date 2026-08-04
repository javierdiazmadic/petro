"""API routes for model explainability using SHAP."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
import numpy as np

from petro.core import get_logger
from petro.ml.explainability.shap_explainer import SHAPExplainer
from petro.ml.inference import InferencePipeline

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["explainability"])


@router.get("/explain/feature-importance")
async def get_feature_importance_shap(
    top_n: int = 10,
) -> dict:
    """Get feature importance using SHAP values.

    SHAP (SHapley Additive exPlanations) provides theoretically sound
    feature importance by computing contribution of each feature to
    the prediction.

    Args:
        top_n: Number of top features to return

    Returns:
        Dictionary with feature importance ranking
    """
    try:
        # Initialize pipeline and get model
        pipeline = InferencePipeline()
        pipeline.initialize("petro-fuel-prediction")

        if not pipeline.is_ready():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Model not available",
                    "error_code": "MODEL_NOT_AVAILABLE",
                },
            )

        # Create SHAP explainer
        model = pipeline.predictor.model
        explainer = SHAPExplainer(model, model_type="xgboost")

        # Generate dummy data for explanation (in production, use actual training data)
        dummy_features = np.random.randn(100, 15)
        feature_names = [
            "price_momentum_10d",
            "brent_price",
            "volatility_7d",
            "news_sentiment",
            "day_of_week",
            "month",
            "rsi_14",
            "macd",
            "bollinger_band_position",
            "price_ma_7d",
            "price_lag_1d",
            "wti_price",
            "eurusd_ratio",
            "inventory_eia",
            "hour",
        ]

        # Get summary plot data
        summary = explainer.summary_plot_data(dummy_features, feature_names)

        if not summary:
            raise HTTPException(status_code=500, detail="SHAP calculation failed")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "method": "SHAP TreeExplainer",
            "model_type": "xgboost",
            "feature_importance": summary["feature_importance"][:top_n],
            "total_features": summary["total_features"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in SHAP explanation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Explainability service unavailable")


@router.post("/explain/single")
async def explain_single_prediction(
    features: List[float],
) -> dict:
    """Generate SHAP explanation for a single prediction.

    Shows how each feature contributes to the model's prediction
    (positive contribution = pushes prediction up, negative = pushes down).

    Args:
        features: Feature vector for prediction

    Returns:
        SHAP values and feature contributions
    """
    try:
        if len(features) != 15:
            raise HTTPException(
                status_code=422,
                detail="Expected 15 features",
            )

        # Initialize explainer
        pipeline = InferencePipeline()
        pipeline.initialize("petro-fuel-prediction")

        model = pipeline.predictor.model
        explainer = SHAPExplainer(model, model_type="xgboost")

        feature_names = [
            "price_momentum_10d",
            "brent_price",
            "volatility_7d",
            "news_sentiment",
            "day_of_week",
            "month",
            "rsi_14",
            "macd",
            "bollinger_band_position",
            "price_ma_7d",
            "price_lag_1d",
            "wti_price",
            "eurusd_ratio",
            "inventory_eia",
            "hour",
        ]

        features_array = np.array(features).reshape(1, -1)
        explanation = explainer.explain_single(features_array, feature_names)

        if not explanation:
            raise HTTPException(status_code=500, detail="SHAP calculation failed")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "prediction": explanation["prediction"],
            "base_value": explanation["base_value"],
            "feature_contributions": [
                {
                    "feature": f["name"],
                    "contribution": f["shap_value"],
                    "feature_value": f["feature_value"],
                }
                for f in explanation["feature_importance"][:10]
            ],
            "method": "SHAP TreeExplainer",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining single prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Explainability service unavailable")
