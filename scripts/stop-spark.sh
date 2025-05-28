#!/bin/bash
ENV=${1:-local}

# Get the root directory of the project
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Export SPARK_ENV for docker-compose
export SPARK_ENV=${ENV}

# Stop everything with a single command
docker-compose -f docker-compose.yml -f docker-compose.${ENV}.yml \
  -f docker-compose.worker2.yml -f docker-compose.worker3.yml \
  --project-name spark-engine down

# Remove the network
docker network rm spark-engine_spark_network || true

echo "All Spark services have been stopped successfully."
