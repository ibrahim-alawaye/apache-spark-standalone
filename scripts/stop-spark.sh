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

# Clean up unused containers and networks
docker container prune -f
docker network prune -f

# Remove unused volumes
docker volume prune -f

# Clean up temporary files
rm -rf /tmp/spark-events/*
rm -rf /tmp/spark-checkpoints/*

echo "All Spark services have been stopped and cleaned up successfully."
