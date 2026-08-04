from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20


class RedisSettings(BaseSettings):
    url: str
    db: int = 0
    ttl_seconds: int = 3600


class CelerySettings(BaseSettings):
    broker_url: str
    result_backend: str
    timezone: str = "UTC"
    enable_utc: bool = True
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: List[str] = ["json"]


class MLflowSettings(BaseSettings):
    tracking_uri: str = "http://localhost:5000"
    artifact_root: str = "/mlflow/artifacts"
    experiment_name: str = "petro-production"


class MLSettings(BaseSettings):
    model_path: str = "models/production/price_model.pkl"
    scaler_path: str = "models/production/scaler.pkl"
    prediction_horizon_days: int = 7


class NLPSettings(BaseSettings):
    model_size: str = "full"  # full | lite
    enable_transformers: bool = True
    bert_model: str = "bert-base-multilingual-cased"
    embedding_model: str = "sentence-transformers/all-MiniLM-l12-v2"
    spacy_models: List[str] = ["es_core_news_sm", "en_core_web_sm"]


class LoggingSettings(BaseSettings):
    level: str = "INFO"
    format: str = "json"  # json | text


class APISettings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    cors_origins: List[str] = ["*"]
    title: str = "PETRO API"
    version: str = "0.1.0"
    description: str = "Sistema de predicción del precio de gasolina y gasóleo en España"


class GPUSettings(BaseSettings):
    enable: bool = True
    device: str = "cuda:0"
    memory_fraction: float = 0.8


class FeaturesSettings(BaseSettings):
    recalc_interval_minutes: int = 15
    cache_ttl_seconds: int = 600


class PredictionSettings(BaseSettings):
    enable_explainability: bool = True
    batch_size: int = 32


class ConnectorsSettings(BaseSettings):
    brent_enabled: bool = True
    wti_enabled: bool = True
    eurusd_enabled: bool = True
    geoportal_enabled: bool = True
    rss_news_enabled: bool = True


class Settings(BaseSettings):
    env: str = "development"
    debug: bool = False

    database: DatabaseSettings
    redis: RedisSettings
    celery: CelerySettings
    mlflow: MLflowSettings
    ml: MLSettings
    nlp: NLPSettings
    logging: LoggingSettings
    api: APISettings
    gpu: GPUSettings
    features: FeaturesSettings
    prediction: PredictionSettings
    connectors: ConnectorsSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
    )


settings = Settings()
