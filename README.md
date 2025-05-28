# SME Spark-Engine Standalone Data Processing

A comprehensive Apache Spark cluster setup for data processing and analytics, packaged with Docker for easy deployment in both local development and production environments.

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## Overview

OX-PCA Spark Engine provides a ready-to-use Apache Spark cluster with the following components:
- Spark Master and Worker nodes
- Redis for distributed caching
- MinIO for S3-compatible object storage
- Prometheus and Grafana for monitoring
- JMX exporter for exposing metrics

The system is designed for scalability and can be configured for both local development and production deployments.

## Screenshots

### Spark Master
![Spark Master UI - Cluster Overview](images/Screenshot%202025-05-28%20012954.png)
*The Spark Master web interface showing cluster resources and connected workers*

### Worker Details
![Worker Details - Resource Allocation](images/Screenshot%202025-05-28%20013022.png)
*Detailed view of worker nodes showing CPU, memory allocation and running executors*

### Execution Dashboard
![Execution Dashboard - Job Monitoring](images/Screenshot%202025-05-28%20013053.png)
*Dashboard for monitoring active Spark applications and their execution metrics*

### Performance Metrics
![Performance Metrics - Grafana Integration](images/Screenshot%202025-05-28%20013116.png)
*Grafana dashboard displaying real-time performance metrics from the Spark cluster*

## System Requirements

### Recommended Hardware
- **CPU**: 4+ cores (8+ threads)
- **RAM**: 16GB minimum (8GB for Spark)
- **Storage**: 10GB+ free space

### Software Prerequisites
- Docker and Docker Compose
- Git
- Bash shell

## Quick Start

### Clone the Repository

```bash
git clone https://github.com/ibrahim-alawaye/apache-spark-standalone.git
cd apache-spark-standalone
```

### Start the Spark Cluster

For local development:
```bash
sudo ./scripts/start-spark.sh local
```

For production:
```bash
sudo ./scripts/start-spark.sh prod
```

### Stop the Spark Cluster

```bash
sudo ./scripts/stop-spark.sh local  # or 'prod' for production
```

### Access the UI Interfaces

- **Spark Master**: http://localhost:8080
- **Spark Worker**: http://localhost:8081
- **Grafana**: http://localhost:3000 (default: admin/admin)
- **Prometheus**: http://localhost:9090
- **MinIO Console**: http://localhost:9001 (default: minio/123456789)

## Architecture

The cluster consists of the following component:

### Spark Master
- Coordinates the cluster
- Exposes web UI on port 8080
- JMX metrics exposed on port 9091

### Spark Workers (3 instances)
- Execute Spark tasks
- Each worker has its own IP address:
  - Worker 1: 172.20.0.3
  - Worker 2: 172.20.0.10
  - Worker 3: 172.20.0.11
- Each worker can host multiple executors

### Redis
- Provides caching functionality
- Runs on 172.20.0.4:6379

### MinIO
- S3-compatible object storage
- Access via port 9000
- Web console on port 9001

### Monitoring
- Prometheus collects metrics from all components
- Grafana provides visualization dashboards
- JMX exporter bridges JVM metrics to Prometheus

## Configuration

### Environment-Specific Configuration

Configuration files are stored in the `config/` directory:
- `config/local/` - Development environment settings
- `config/prod/` - Production environment settings

Each environment has an `.env` file with resource settings:

```
# Resource Configuration
SPARK_DRIVER_MEMORY=1g
SPARK_DRIVER_CORES=1
SPARK_EXECUTOR_MEMORY=512m
SPARK_EXECUTOR_CORES=1
SPARK_EXECUTOR_INSTANCES=2
SPARK_WORKER_MEMORY=2g
SPARK_WORKER_CORES=2
```

### Adjusting Resources

For laptops or lower-resource environments, use:
```
SPARK_DRIVER_MEMORY=1g
SPARK_DRIVER_CORES=1
SPARK_EXECUTOR_MEMORY=384m
SPARK_EXECUTOR_INSTANCES=1
SPARK_WORKER_MEMORY=1g
SPARK_WORKER_CORES=1
```

For high-performance environments:
```
SPARK_DRIVER_MEMORY=4g
SPARK_DRIVER_CORES=2
SPARK_EXECUTOR_MEMORY=2g
SPARK_EXECUTOR_CORES=2
SPARK_EXECUTOR_INSTANCES=4
SPARK_WORKER_MEMORY=8g
SPARK_WORKER_CORES=4
```

## Monitoring

### Metrics Collection

Prometheus collects metrics from:
- Spark Master (172.20.0.2:8080)
- Spark Workers (172.20.0.3/10/11:8081)
- Spark Applications (172.20.0.2:4040)

### Dashboards

The Grafana instance comes pre-configured with dashboards for:
- Spark cluster overview
- Worker node metrics
- Application performance
- JVM statistics

## Troubleshooting

### Common Issues

#### Port Conflicts
If you encounter port conflicts, modify the port mappings in `docker-compose.yml`.

#### Network Issues
If you see "network already exists" or "address already in use" errors:
```bash
docker network prune -f
```

#### Worker Not Starting
Check logs with:
```bash
docker logs spark-engine-spark-worker-1
```

### Logs

Container logs are available via Docker:
```bash
docker logs spark-master
docker logs spark-engine-spark-worker-1
```

Spark event logs are stored in `/tmp/spark-events/`.

## Development

### Adding Jars

Place additional JAR files in the `jars/` directory.

### Submitting Jobs

Sample jobs are located in `job-samples/`. To submit a job:

```bash
docker exec spark-master /opt/spark/bin/spark-submit \
--master spark://172.20.0.2:7077 \
/opt/spark/job-samples/generate_data.py
```

### Scaling the Cluster

To adjust the number of workers, modify the `scripts/start-spark.sh` script and the relevant docker-compose files.


For more information or support, contact mailto:ibalawaye@gmail.com or open an issue on the repository.
