# SME Spark-Engine Standalone Data Processing with Prefect Orchestration

A comprehensive Apache Spark cluster setup with Prefect workflow orchestration for data processing and analytics, packaged with Docker for easy deployment in both local development and production environments.
<img width="2323" height="1232" alt="Blank diagram" src="https://github.com/user-attachments/assets/fe560597-71f5-4566-ad64-9851da3be140" />


## Overview

Spark Engine provides a ready-to-use Apache Spark cluster with advanced workflow orchestration capabilities:

### Core Components
- **Apache Spark Master and Worker nodes**
- **Prefect Server and Workers** for workflow orchestration
- **Redis** for distributed caching
- **MinIO** for S3-compatible object storage
- **Prometheus and Grafana** for monitoring
- **JMX exporter** for exposing metrics

### Prefect Integration
- **Automated job scheduling** with cron-based triggers
- **Workflow orchestration** for complex data pipelines
- **Remote deployment** capabilities
- **Real-time monitoring** and logging
- **Error handling and retries**

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
- **CPU**: 6+ cores (12+ threads) - *increased for Prefect workers*
- **RAM**: 20GB minimum (12GB for Spark + 8GB for Prefect)
- **Storage**: 15GB+ free space

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

### Start the Complete Stack

#### Option 1: Spark + Prefect (Recommended)
```bash
# Start Spark cluster first
sudo ./scripts/start-spark.sh local

# Start Prefect orchestration
docker-compose -f docker-compose.prefect.yml --project-name spark-engine up -d
```

#### Option 2: Spark Only
```bash
# For Spark-only deployment
sudo ./scripts/start-spark.sh local
```

### Stop the Stack

```bash
# Stop Prefect
docker-compose -f docker-compose.prefect.yml --project-name spark-engine down

# Stop Spark
sudo ./scripts/stop-spark.sh local
```

### Access the UI Interfaces

#### Spark Interfaces
- **Spark Master**: http://localhost:8080
- **Spark Worker**: http://localhost:8081

#### Prefect Interfaces
- **Prefect Server UI**: http://localhost:4200
- **Prefect API**: http://localhost:4200/api

#### Monitoring & Storage
- **Grafana**: http://localhost:3000 (default: admin/admin)
- **Prometheus**: http://localhost:9090
- **MinIO Console**: http://localhost:9001 (default: minio/123456789)

## Architecture

### Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Spark + Prefect Ecosystem                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐                   │
│  │   Prefect UI    │    │  Prefect Server  │                   │
│  │   :4200         │◄───┤  API & Scheduler │                   │
│  └─────────────────┘    └──────────────────┘                   │
│                                   │                             │
│  ┌─────────────────┐    ┌──────────▼──────┐                   │
│  │ Prefect Worker-1│    │ Prefect Worker-2│                   │
│  │ Flow Execution  │    │ Flow Execution  │                   │
│  └─────────┬───────┘    └─────────┬───────┘                   │
│            │                      │                           │
│            └──────────┬───────────┘                           │
│                       │ SSH                                   │
│  ┌────────────────────▼────────────────────┐                 │
│  │            Spark Master                 │                 │
│  │         :8080 (UI) :7077 (API)         │                 │
│  └─────────────────┬───────────────────────┘                 │
│                    │                                         │
│  ┌─────────────────▼─────────────────┐                       │
│  │         Spark Workers             │                       │
│  │    Worker-1  Worker-2  Worker-3   │                       │
│  │      :8081     :8082     :8083    │                       │
│  └───────────────────────────────────┘                       │
│                                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Network Architecture

All components communicate via the `spark_network` (172.20.0.0/24):

```
┌─────────────────────────────────────────────────────────────┐
│                    Network: 172.20.0.0/24                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Spark Components:                                          │
│  ├─ Spark Master:    172.20.0.2                            │
│  ├─ Spark Worker-1:  172.20.0.3                            │
│  ├─ Spark Worker-2:  172.20.0.10                           │
│  └─ Spark Worker-3:  172.20.0.11                           │
│                                                             │
│  Prefect Components:                                        │
│  ├─ Database:        172.20.0.30                           │
│  ├─ Prefect Server:  172.20.0.31                           │
│  ├─ Worker-1:        172.20.0.32                           │
│  ├─ Worker-2:        172.20.0.33                           │
│  ├─ Worker-3:        172.20.0.34                           │
│  └─ CLI:             172.20.0.35                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Prefect-Spark Integration

The integration works through SSH connectivity:

1. **Prefect Workers** execute workflow tasks
2. **SSH Connection** to Spark Master (172.20.0.2)
3. **Spark Job Submission** via `spark-submit`
4. **Result Collection** and status reporting

#### SSH Configuration
```bash
# Credentials (configured in Dockerfile.prefect)
SPARK_HOST=172.20.0.2
SPARK_USER=root
SPARK_PASS=sparkpass
SPARK_PORT=22
```

## Configuration

### Environment-Specific Configuration

Configuration files are stored in the `config/` directory:
- `config/local/` - Development environment settings
- `config/prod/` - Production environment settings

#### Spark Configuration
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

#### Prefect Configuration
```yaml
# Prefect Server Settings
PREFECT_SERVER_API_HOST=0.0.0.0
PREFECT_SERVER_API_PORT=4200
PREFECT_API_DATABASE_CONNECTION_URL=postgresql+asyncpg://postgres:postgres@172.20.0.30:5432/prefect
PREFECT_SERVER_ALLOW_EPHEMERAL_MODE=false

# Worker Settings
PREFECT_WORKER_HEARTBEAT_SECONDS=30
PREFECT_WORKER_QUERY_SECONDS=10
PREFECT_WORKER_PREFETCH_SECONDS=10
```

### Adjusting Resources

#### For Development (Low Resources)
```yaml
# Reduce worker count and memory
worker-1:
  environment:
    - SPARK_EXECUTOR_MEMORY=384m
    - SPARK_DRIVER_MEMORY=512m
```

#### For Production (High Performance)
```yaml
# Increase resources and add more workers
worker-4:
  # Add additional worker instances
  environment:
    - SPARK_EXECUTOR_MEMORY=2g
    - SPARK_DRIVER_MEMORY=2g
```

## Workflow Management

### Creating and Deploying Flows

#### 1. **Create a Flow** (`flows/my_pipeline.py`)
```python
from prefect import flow, task
from spark_init import copy_and_submit_python_job

@task
def run_data_processing():
    return copy_and_submit_python_job(
        local_python_file="my_spark_job.py",
        spark_args={"executor-memory": "1g"}
    )

@flow
def my_data_pipeline():
    result = run_data_processing()
    return result
```

#### 2. **Deploy the Flow**
```bash
# Navigate to flows directory
cd flows

# Use the deployment script
./deploy_remote_advanced.sh

# Or deploy manually
docker exec spark-engine-worker-1-1 prefect deploy my_pipeline.py:my_data_pipeline --name my-pipeline --cron "0 9 * * *"
```

#### 3. **Monitor Execution**
- **Prefect UI**: http://localhost:4200
- **Flow Runs**: View execution status and logs
- **Deployments**: Manage scheduled workflows

### Available Deployment Scripts

#### `deploy_remote_advanced.sh`
Interactive deployment script with options:
1. **Pre-configured deployment** - Quick deploy common flows
2. **Custom deployment** - Deploy any flow with custom settings
3. **Interactive shell** - Access worker shell directly
4. **List existing deployments** - View all deployed flows

#### Example Usage
```bash
./deploy_remote_advanced.sh

# Choose option 2 (Custom deployment)
Enter flow file: data_pipeline2_flow.py
Enter flow function: data_pipeline_flow
Enter deployment name: daily-etl-pipeline
Enter schedule: 0 9 * * *  # Daily at 9 AM
```

### Flow Examples

#### Simple Data Pipeline
```python
@flow
def simple_etl():
    return copy_and_submit_python_job("etl_job.py")
```

#### Complex Multi-Stage Pipeline
```python
@flow
def complex_pipeline():
    # Extract
    raw_data = extract_data()
    
    # Transform
    clean_data = transform_data(raw_data)
    
    # Load
    result = load_data(clean_data)
    
    # Validate
    validate_results(result)
    
    return result
```

## Monitoring

### Prefect Monitoring

#### Prefect UI Dashboard
- **URL**: http://localhost:4200
- **Features**:
  - Flow run status and history
  - Real-time execution logs
  - Deployment management
  - Worker status monitoring
  - Performance metrics

#### Key Metrics
- **Flow Success Rate**: Percentage of successful runs
- **Execution Time**: Average and peak execution times
- **Worker Utilization**: Active vs idle workers
- **Queue Status**: Pending and running tasks

### Spark Monitoring

#### Metrics Collection
Prometheus collects metrics from:
- Spark Master (172.20.0.2:8080)
- Spark Workers (172.20.0.3/10/11:8081)
- Spark Applications (172.20.0.2:4040)

#### Grafana Dashboards
Pre-configured dashboards for:
- Spark cluster overview
- Worker node metrics
- Application performance
- JVM statistics
- **Prefect integration metrics**

### Combined Monitoring Strategy

````bash
# Check overall system health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Monitor Prefect workers
docker exec spark-engine-worker-1-1 prefect worker status

# Check Spark cluster
curl -s http://localhost:8080/api/v1/applications | jq '.[].name'

### Debug Commands

#### Prefect Debugging
```bash
# Access Prefect CLI
docker exec -it spark-engine-cli-1 bash

# Check worker status
prefect worker status

# List all deployments
prefect deployment ls

# View flow runs
prefect flow-run ls --limit 10

# Check server health
prefect server status

# View worker logs in real-time
docker logs -f spark-engine-worker-1-1
```

#### Spark Debugging
```bash
# Check Spark master status
curl -s http://localhost:8080/api/v1/applications

# View Spark worker logs
docker logs spark-worker-1

# Test Spark job submission
docker exec spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 /opt/spark/examples/src/main/python/pi.py
```

#### Network Debugging
```bash
# Test network connectivity
docker exec spark-engine-worker-1-1 ping spark-master
docker exec spark-engine-worker-1-1 ping 172.20.0.31

# Check port accessibility
docker exec spark-engine-worker-1-1 nc -zv 172.20.0.2 22
docker exec spark-engine-worker-1-1 nc -zv 172.20.0.31 4200
```

### Log Locations

#### Container Logs
```bash
# Prefect Server
docker logs spark-engine-server-1

# Prefect Workers
docker logs spark-engine-worker-1-1
docker logs spark-engine-worker-2-1
docker logs spark-engine-worker-3-1

# Database
docker logs spark-engine-database-1

# Spark Components
docker logs spark-master
docker logs spark-worker-1
```

#### Application Logs
```bash
# Spark event logs
docker exec spark-master ls -la /tmp/spark-events/

# Prefect flow logs (via UI)
# http://localhost:4200/flow-runs

# System logs
docker exec spark-engine-worker-1-1 tail -f /var/log/syslog
```

## Development

### Development Workflow

#### 1. **Local Development Setup**
```bash
# Clone repository
git clone https://github.com/ibrahim-alawaye/apache-spark-standalone.git
cd apache-spark-standalone

# Start development environment
sudo ./scripts/start-spark.sh local
docker-compose -f docker-compose.prefect.yml up -d
```
