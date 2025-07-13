from prefect import flow, task
from spark_init import run_spark_job, run_spark_pi, test_spark

@task
def test_connection():
    print("🔍 Testing Spark connection...")
    return test_spark()

@task  
def run_pi_job():
    print("🧮 Running Spark Pi...")
    return run_spark_pi(5)

@task
def run_custom_job():
    print("☕ Running custom Spark job...")
    # Example: Run any Spark job by providing the path
    return run_spark_job(
        "/opt/spark/examples/jars/spark-examples_2.12-3.5.0.jar",
        "--class org.apache.spark.examples.JavaWordCount /opt/spark/README.md"
    )

@flow
def simple_spark_flow():
    # Test connection
    if not test_connection():
        print("❌ Connection failed!")
        return False
    
    # Run Pi job
    if not run_pi_job():
        print("❌ Pi job failed!")
        return False
        
    # Run custom job
    if not run_custom_job():
        print("❌ Custom job failed!")
        return False
    
    print("✅ All jobs completed!")
    return True

if __name__ == "__main__":
    result = simple_spark_flow()
    print(f"Final result: {result}")
