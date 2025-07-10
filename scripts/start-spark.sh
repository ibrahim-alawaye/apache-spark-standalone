#!/bin/bash
ENV=${1:-local}

python3 scripts/download_jars.py

# Get the root directory of the project
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Export SPARK_ENV for docker-compose
export SPARK_ENV=${ENV}

# Source the environment file
set -a
source "${ROOT_DIR}/config/${ENV}/.env.${ENV}"
set +a

# Create network first (if it doesn't exist)
docker network create --subnet=172.20.0.0/16 spark-engine_spark_network || true

# Start Spark cluster and Prefect services together using the same project
docker-compose -f docker-compose.yml -f docker-compose.${ENV}.yml \
  -f docker-compose.worker2.yml -f docker-compose.worker3.yml \
  -f docker-compose.prefect.yml \
  --project-name spark-engine up -d

echo "Started Spark cluster in ${ENV} mode with 3 workers"
echo "Started Prefect server and 3 workers"
echo "Prefect UI available at: http://localhost:4200"
