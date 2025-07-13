from prefect import flow, task
from spark_init import test_spark

@task
def check_spark_health():
    """Check if Spark cluster is healthy."""
    return test_spark()

@task
def check_spark_jobs():
    """Check if we can run a simple Spark job."""
    from spark_init import submit_jar_job
    return submit_jar_job(
        jar_file="/opt/spark/examples/jars/spark-examples_2.12-3.5.0.jar",
        main_class="org.apache.spark.examples.SparkPi",
        app_args=["2"],
        spark_args={"executor-memory": "512m"}
    )

@flow
def spark_health_flow():
    """Health check flow for Spark cluster."""
    print("🔍 Checking Spark health...")
    
    # Check connection
    health = check_spark_health()
    print(f"Connection health: {health}")
    
    if health:
        # Run a simple job test
        job_health = check_spark_jobs()
        print(f"Job execution health: {job_health}")
        return health and job_health
    
    return False

if __name__ == "__main__":
    result = spark_health_flow()
    print(f"Health check result: {result}")