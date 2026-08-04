# PHASE 12: Cloud Deployment on GCP
# Terraform configuration for PETRO system on Google Cloud Platform

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "petro-terraform-state"
    prefix = "prod"
  }
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

# ===== Cloud SQL (PostgreSQL + TimescaleDB) =====

resource "google_sql_database_instance" "petro_db" {
  name             = "petro-prod-db-${var.environment}"
  database_version = "POSTGRES_16"
  region           = var.gcp_region

  settings {
    tier              = "db-custom-2-8192" # 2 vCPU, 8GB RAM
    availability_type = "REGIONAL"
    backup_configuration {
      enabled  = true
      location = var.gcp_region
    }
    ip_configuration {
      require_ssl = true
    }
  }

  deletion_protection = true
}

resource "google_sql_database" "petro" {
  name     = "petro"
  instance = google_sql_database_instance.petro_db.name
}

resource "google_sql_user" "petro_user" {
  name     = "petro"
  instance = google_sql_database_instance.petro_db.name
  password = var.db_password
}

# ===== Cloud Memorystore (Redis) =====

resource "google_redis_instance" "petro_cache" {
  name           = "petro-prod-redis-${var.environment}"
  memory_size_gb = 5
  region         = var.gcp_region
  tier           = "basic"
  redis_version  = "7.0"

  auth_enabled = true
}

# ===== Cloud Storage (Model artifacts) =====

resource "google_storage_bucket" "petro_models" {
  name          = "petro-models-${var.gcp_project}"
  location      = var.gcp_region
  force_destroy = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 10
    }
    action {
      type = "Delete"
    }
  }
}

# ===== Cloud Run (FastAPI application) =====

resource "google_cloud_run_service" "petro_api" {
  name     = "petro-api-${var.environment}"
  location = var.gcp_region

  template {
    spec {
      containers {
        image = "gcr.io/${var.gcp_project}/petro:${var.app_version}"

        env {
          name  = "SQLALCHEMY_DATABASE_URL"
          value = "postgresql+asyncpg://${google_sql_user.petro_user.name}:${var.db_password}@${google_sql_database_instance.petro_db.private_ip_address}/petro"
        }

        env {
          name  = "REDIS_URL"
          value = "redis://:${google_redis_instance.petro_cache.auth_string}@${google_redis_instance.petro_cache.host}:${google_redis_instance.petro_cache.port}"
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "DEBUG"
          value = "false"
        }

        resources {
          limits = {
            memory = "2Gi"
            cpu    = "2"
          }
        }
      }

      service_account_name = google_service_account.petro_api.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_sql_database_instance.petro_db,
    google_redis_instance.petro_cache,
  ]
}

resource "google_cloud_run_service_iam_member" "public_access" {
  service = google_cloud_run_service.petro_api.name
  role    = "roles/run.invoker"
  member  = "allUsers"
  location = var.gcp_region
}

# ===== Service Accounts =====

resource "google_service_account" "petro_api" {
  account_id   = "petro-api-${var.environment}"
  display_name = "PETRO API Service Account"
}

resource "google_project_iam_member" "storage_access" {
  project = var.gcp_project
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.petro_api.email}"
}

# ===== Cloud Scheduler (Celery Beat alternative) =====

resource "google_cloud_scheduler_job" "petro_pipeline" {
  name            = "petro-pipeline-15min"
  description     = "Trigger PETRO pipeline every 15 minutes"
  schedule        = "*/15 * * * *"
  time_zone       = "UTC"
  region          = var.gcp_region
  attempt_deadline = "320s"

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.petro_api.status[0].url}/scheduler/trigger-pipeline"

    oidc_token {
      service_account_email = google_service_account.petro_api.email
    }
  }
}

resource "google_cloud_scheduler_job" "petro_retrain" {
  name            = "petro-daily-retrain"
  description     = "Retrain models daily at 2 AM UTC"
  schedule        = "0 2 * * *"
  time_zone       = "UTC"
  region          = var.gcp_region
  attempt_deadline = "3600s"

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.petro_api.status[0].url}/scheduler/trigger-training"

    oidc_token {
      service_account_email = google_service_account.petro_api.email
    }
  }
}

# ===== Monitoring =====

resource "google_monitoring_uptime_check_http" "petro_health" {
  display_name = "PETRO API Health Check"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path = "/api/v1/health"
    port = 443
  }

  monitored_resource {
    type = "uptime-url"
    labels = {
      host = trimprefix(google_cloud_run_service.petro_api.status[0].url, "https://")
    }
  }
}

resource "google_monitoring_alert_policy" "petro_down" {
  display_name = "PETRO API Down"
  combiner     = "OR"

  conditions {
    display_name = "API Health Check Failed"

    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" resource.type=\"uptime-url\" resource.label.host=\"${trimprefix(google_cloud_run_service.petro_api.status[0].url, "https://")}\" metric.label.check_id=\"${google_monitoring_uptime_check_http.petro_health.uptime_check_id}\""
      duration        = "300s"
      comparison      = "COMPARISON_LT"
      threshold_value = 0.5
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]
}

resource "google_monitoring_notification_channel" "email" {
  display_name = "PETRO Alert Email"
  type         = "email"
  enabled      = true

  labels = {
    email_address = var.alert_email
  }
}

# ===== Outputs =====

output "api_url" {
  value       = google_cloud_run_service.petro_api.status[0].url
  description = "PETRO API URL"
}

output "database_private_ip" {
  value       = google_sql_database_instance.petro_db.private_ip_address
  description = "PostgreSQL Database private IP"
}

output "redis_host" {
  value       = google_redis_instance.petro_cache.host
  description = "Redis Cache host"
}

output "models_bucket" {
  value       = google_storage_bucket.petro_models.name
  description = "GCS bucket for model artifacts"
}
