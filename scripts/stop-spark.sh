#!/bin/bash
ENV=${1:-local}

# Get the root directory of the project
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Export SPARK_ENV for docker-compose
export SPARK_ENV=${ENV}

# Stop all services (Spark cluster and Prefect) using the same project
docker-compose -f docker-compose.yml -f docker-compose.${ENV}.yml \
  -f docker-compose.worker2.yml -f docker-compose.worker3.yml \
  -f docker-compose.prefect.yml \
  --project-name spark-engine down

# Remove the network
docker network rm spark-engine_spark_network || true

# Clean up unused containers and networks
docker container prune -f
docker network prune -f

# Remove unused volumes (optional - comment out if you want to keep data)
docker volume prune -f

# Clean up temporary files
rm -rf /tmp/spark-events/* 2>/dev/null || true
rm -rf /tmp/spark-checkpoints/* 2>/dev/null || true

echo "All Spark and Prefect services have been stopped and cleaned up successfully."
