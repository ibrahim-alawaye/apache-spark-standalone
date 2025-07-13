# Prefect Flows for Apache Spark Standalone

A comprehensive workflow orchestration system using Prefect 3.x to manage and deploy Apache Spark jobs in a containerized environment.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Flow Design Guide](#flow-design-guide)
- [Deployment Options](#deployment-options)
- [Available Flows](#available-flows)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Overview

This system provides:
- **Automated Spark job deployment** via Prefect workflows
- **Scheduled execution** with cron-based scheduling
- **Remote deployment** from local machine to Spark cluster
- **Health monitoring** and anomaly detection
- **Interactive deployment interface** for easy management

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Local Dev     │    │  Prefect Worker  │    │  Spark Master   │
│                 │───▶│                  │───▶│                 │
│ deploy_remote.sh│    │ flows/*.py       │    │ spark-jobs/     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Deploy a Flow

```bash
# Make the deployment script executable
chmod +x deploy_remote_advanced.sh

# Run the deployment interface
./deploy_remote_advanced.sh
```

### 2. Choose Deployment Option

```
🎛️ Deployment Options:
======================
1. Pre-configured deployment    # Quick deploy common flows
2. Custom deployment           # Deploy any flow with custom settings
3. Interactive shell          # Access worker shell directly
4. List existing deployments # View all deployed flows
```

### 3. Example Deployment

```bash
# Option 2: Custom deployment
Enter flow file: data_pipeline2_flow.py
Enter flow function: data_pipeline_flow
Enter deployment name: my-data-pipeline
Enter schedule: 0 9 * * *  # Daily at 9 AM

# Deployment will be created with ID and accessible via Prefect UI
```

## Flow Design Guide

### Basic Flow Structure

```python
from prefect import flow, task
from spark_init import copy_and_submit_python_job

@task
def run_spark_job():
    """Task to execute Spark job."""
    return copy_and_submit_python_job(
        local_python_file="my_spark_job.py",
        spark_args={"executor-memory": "1g", "driver-memory": "512m"}
    )

@flow
def my_data_pipeline_flow():
    """Main flow orchestrating the pipeline."""
    result = run_spark_job()
    return result

if __name__ == "__main__":
    # Allow direct execution for testing
    result = my_data_pipeline_flow()
    print(f"Pipeline result: {result}")
```

### Advanced Flow Example

Looking at `flows/data_pipeline2_flow.py`:

```python
from prefect import flow, task
from spark_init import copy_and_submit_python_job

@task
def run_data_pipeline():
    """Execute the main data processing pipeline."""
    return copy_and_submit_python_job(
        local_python_file="data_pipeline2.py",
        spark_args={"spark.sql.adaptive.enabled": "true"}
    )

@flow
def data_pipeline_flow():
    """
    Data Pipeline Flow
    
    This flow:
    1. Copies the Python job to Spark master
    2. Submits the job for execution
    3. Returns the execution result
    """
    pipeline_result = run_data_pipeline()
    return pipeline_result

if __name__ == "__main__":
    result = data_pipeline_flow()
    print(f"Pipeline result: {result}")
```

### Flow Design Best Practices

#### 1. **Task Decomposition**
```python
@task
def extract_data():
    """Extract data from source."""
    pass

@task
def transform_data():
    """Transform the extracted data."""
    pass

@task
def load_data():
    """Load data to destination."""
    pass

@flow
def etl_pipeline():
    """Complete ETL pipeline."""
    raw_data = extract_data()
    clean_data = transform_data()
    result = load_data()
    return result
```

#### 2. **Error Handling**
```python
@task(retries=3, retry_delay_seconds=60)
def resilient_spark_job():
    """Spark job with automatic retries."""
    try:
        return copy_and_submit_python_job("my_job.py")
    except Exception as e:
        print(f"Job failed: {e}")
        raise
```

#### 3. **Parameterization**
```python
@flow
def parameterized_pipeline(
    input_path: str = "/tmp/input",
    output_path: str = "/tmp/output",
    executor_memory: str = "1g"
):
    """Pipeline with configurable parameters."""
    spark_args = {
        "executor-memory": executor_memory,
        "conf": f"spark.sql.warehouse.dir={output_path}"
    }
    return copy_and_submit_python_job("pipeline.py", spark_args)
```

#### 4. **Complex Workflows**
```python
@flow
def complex_data_pipeline():
    """Multi-stage data pipeline."""
    
    # Parallel data extraction
    sales_data = extract_sales_data()
    customer_data = extract_customer_data()
    
    # Sequential processing
    merged_data = merge_datasets(sales_data, customer_data)
    analytics_result = run_analytics(merged_data)
    
    # Conditional execution
    if analytics_result.success:
        generate_reports(analytics_result)
    
    return analytics_result
```

## Deployment Options

### 1. Pre-configured Deployments

Quick deployment of common flows:

```bash
./deploy_remote_advanced.sh
# Choose option 1
# Select from: --data-pipeline, --health-check, --simple
```

### 2. Custom Deployments

Deploy any flow with custom configuration:

```bash
./deploy_remote_advanced.sh
# Choose option 2
# Specify: flow_file, flow_function, deployment_name, schedule
```

### 3. Schedule Formats

```bash
# Every day at 9 AM
0 9 * * *

# Every 15 minutes
*/15 * * * *

# Every Monday at 6 AM
0 6 * * 1

# Every hour on weekdays
0 * * * 1-5

# No schedule (manual trigger only)
# Leave empty
```

## Available Flows

### 1. Data Pipeline Flow (`data_pipeline2_flow.py`)
- **Purpose**: Execute complex data processing jobs
- **Function**: `data_pipeline_flow`
- **Features**: Adaptive query execution, automatic optimization

### 2. Health Check Flow (`health_check_flow.py`)
- **Purpose**: Monitor Spark cluster health
- **Function**: `spark_health_flow`
- **Features**: Connection testing, job execution validation

### 3. Pipeline Workflow (`pipeline_workflow.py`)
- **Purpose**: General-purpose data pipeline
- **Function**: `data_pipeline_flow`
- **Features**: ETL processing, data validation

### 4. Test Job Flow (`test_job_flow.py`)
- **Purpose**: Simple Spark job testing
- **Function**: Varies by implementation
- **Features**: Basic connectivity and execution testing

## Advanced Usage

### Managing Deployments

```bash
# List all deployments
docker exec spark-engine-worker-1-1 prefect deployment ls

# Run a specific deployment
docker exec spark-engine-worker-1-1 prefect deployment run 'data-pipeline-flow/data_pipeline_flow'

# View deployment details
docker exec spark-engine-worker-1-1 prefect deployment inspect <deployment-id>

# Delete a deployment
docker exec spark-engine-worker-1-1 prefect deployment delete <deployment-name>
```

### Monitoring and Logs

```bash
# View worker logs
docker logs spark-engine-worker-1-1

# Access worker shell
docker exec -it spark-engine-worker-1-1 bash

# Check Prefect server status
docker exec spark-engine-worker-1-1 prefect server status
```

### Prefect UI Access

- **URL**: http://172.20.0.31:4200
- **Features**: 
  - Flow run monitoring
  - Deployment management
  - Execution logs
  - Performance metrics

### Creating Custom Spark Jobs

1. **Create your Spark job** (e.g., `my_analysis.py`):
```python
from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder.appName("MyAnalysis").getOrCreate()
    # Your Spark logic here
    spark.stop()

if __name__ == "__main__":
    main()
```

2. **Create a Prefect flow**:
```python
from prefect import flow, task
from spark_init import copy_and_submit_python_job

@task
def run_my_analysis():
    return copy_and_submit_python_job(
        local_python_file="my_analysis.py",
        spark_args={"executor-memory": "2g"}
    )

@flow
def my_analysis_flow():
    return run_my_analysis()
```

3. **Deploy the flow**:
```bash
./deploy_remote_advanced.sh
# Choose custom deployment
# Specify your flow details
```

## Troubleshooting

### Common Issues

#### 1. Deployment Failed
```bash
# Check if file exists
docker exec spark-engine-worker-1-1 ls -la /root/flows/

# Verify flow function name
docker exec spark-engine-worker-1-1 grep -n "def.*flow" /root/flows/your_flow.py
```

#### 2. Spark Job Execution Failed
```bash
# Check Spark connectivity
docker exec spark-engine-worker-1-1 /opt/prefect/spark-ssh.sh test

# View Spark master logs
docker logs spark-master
```

#### 3. Schedule Not Working
```bash
# Verify cron format
echo "0 9 * * *" | crontab -

# Check deployment schedule
docker exec spark-engine-worker-1-1 prefect deployment ls
```

### Debug Commands

```bash
# Test Spark connection
docker exec spark-engine-worker-1-1 python -c "from spark_init import test_spark; print(test_spark())"

# Run flow manually
docker exec spark-engine-worker-1-1 python /root/flows/your_flow.py

# Check Prefect worker status
docker exec spark-engine-worker-1-1 prefect worker status
```

### Getting Help

1. **Check logs**: Always start with container logs
2. **Verify connectivity**: Ensure Spark cluster is running
3. **Test manually**: Run flows directly before deploying
4. **Use interactive shell**: Access worker for debugging

## Examples

### Simple Daily Report
```python
@flow
def daily_report_flow():
    """Generate daily business reports."""
    return copy_and_submit_python_job(
        local_python_file="daily_report.py",
        spark_args={"executor-memory": "1g"}
    )
```

### Complex Analytics Pipeline
```python
@flow
def analytics_pipeline():
    """Multi-stage analytics pipeline."""
    
    # Data ingestion
    raw_data = ingest_data()
    
    # Data processing
    processed_data = process_data(raw_data)
    
    # Analytics
    insights = generate_insights(processed_data)
    
    # Reporting
    create_dashboard(insights)
    
    return insights
```

---

**Need help?** Check the troubleshooting section or access the interactive shell for debugging.

**Prefect UI**: http://172.20.0.31:4200 for visual monitoring and management.