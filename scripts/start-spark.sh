#!/bin/bash
ENV=${1:-local}

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

# Start everything with a single docker-compose command
docker-compose -f docker-compose.yml -f docker-compose.${ENV}.yml \
  -f docker-compose.worker2.yml -f docker-compose.worker3.yml \
  --project-name spark-engine up -d

echo "Started Spark cluster in ${ENV} mode with 3 workers"
