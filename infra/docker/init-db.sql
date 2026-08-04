-- Create MLflow database
CREATE DATABASE IF NOT EXISTS mlflow;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE mlflow TO petro;
