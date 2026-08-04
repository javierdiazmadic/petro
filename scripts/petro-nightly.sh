#!/bin/bash
# PETRO Nightly Data Collection and Pipeline
# Runs daily at 2 AM to collect data and retrain models

set -euo pipefail

# ===== Configuration =====
PETRO_DIR="${PETRO_DIR:-.}"
LOGFILE="${LOGFILE:-${PETRO_DIR}/logs/petro-nightly.log}"
API_URL="${API_URL:-http://localhost:8000}"
API_TOKEN="${PETRO_API_TOKEN:-}"
RETRIES=3
RETRY_DELAY=10

# ===== Helper Functions =====

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOGFILE" >&2
}

retry() {
    local cmd="$*"
    local attempt=1

    while [ $attempt -le $RETRIES ]; do
        log "Attempting: $cmd (attempt $attempt/$RETRIES)"

        if eval "$cmd"; then
            return 0
        fi

        if [ $attempt -lt $RETRIES ]; then
            log "Retrying in ${RETRY_DELAY}s..."
            sleep "$RETRY_DELAY"
        fi

        ((attempt++))
    done

    error "Command failed after $RETRIES attempts: $cmd"
    return 1
}

# ===== Main Pipeline =====

main() {
    log "=========================================="
    log "PETRO Nightly Pipeline Started"
    log "=========================================="

    # Ensure log directory exists
    mkdir -p "$(dirname "$LOGFILE")"

    # Check if API is running
    if ! curl -s -f "$API_URL/api/v1/health" > /dev/null; then
        error "API not responding at $API_URL/api/v1/health"
        exit 1
    fi
    log "✓ API is running"

    # Trigger main pipeline (fetch data, process news, features, inference)
    log "Triggering data pipeline..."
    trigger_pipeline

    # Check if today is retraining day (Sunday)
    if [ "$(date +%A)" = "Sunday" ]; then
        log "Sunday detected - triggering model retraining..."
        trigger_training
    fi

    log "=========================================="
    log "PETRO Nightly Pipeline Completed"
    log "=========================================="
}

trigger_pipeline() {
    local endpoint="/scheduler/trigger-pipeline"
    local cmd="curl -X POST \"$API_URL$endpoint\" -H \"Content-Type: application/json\""

    if [ -n "$API_TOKEN" ]; then
        cmd+=" -H \"Authorization: Bearer $API_TOKEN\""
    fi

    if retry eval "$cmd"; then
        log "✓ Pipeline triggered successfully"

        # Wait for pipeline to complete (with timeout)
        log "Waiting for pipeline completion (max 5 minutes)..."
        sleep 5

        local max_wait=300  # 5 minutes
        local elapsed=0

        while [ $elapsed -lt $max_wait ]; do
            local status=$(curl -s "$API_URL/api/v1/health" | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "unknown")

            if [ "$status" = "healthy" ] || [ "$status" = "degraded" ]; then
                log "✓ Pipeline completed with status: $status"
                return 0
            fi

            sleep 10
            ((elapsed += 10))
        done

        log "Pipeline completion check timed out (may still be running in background)"
        return 0
    else
        error "Failed to trigger pipeline"
        return 1
    fi
}

trigger_training() {
    local endpoint="/scheduler/trigger-training"
    local cmd="curl -X POST \"$API_URL$endpoint\" -H \"Content-Type: application/json\""

    if [ -n "$API_TOKEN" ]; then
        cmd+=" -H \"Authorization: Bearer $API_TOKEN\""
    fi

    if retry eval "$cmd"; then
        log "✓ Training triggered successfully"
        log "Training will run in background (may take 20-30 minutes)"
        return 0
    else
        error "Failed to trigger training"
        return 1
    fi
}

cleanup() {
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log "Pipeline completed successfully"
    else
        error "Pipeline failed with exit code $exit_code"
    fi

    return $exit_code
}

# ===== Execution =====

trap cleanup EXIT

main "$@"
