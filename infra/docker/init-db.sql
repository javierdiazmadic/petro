-- Create MLflow database
CREATE DATABASE mlflow;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE mlflow TO petro;
GRANT ALL PRIVILEGES ON DATABASE petro_dev TO petro;
