from prefect import flow, task
from pyspark.sql import SparkSession
import os

@task
def test_spark_connection():
    """Test Spark connection from Prefect worker"""
    try:
        # Create Spark session
        spark = SparkSession.builder \
            .appName("PrefectSparkTest") \
            .master("spark://172.20.0.2:7077") \
            .config("spark.executor.memory", "1g") \
            .config("spark.driver.memory", "1g") \
            .getOrCreate()
        
        # Create a simple DataFrame
        data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
        columns = ["Name", "Age"]
        df = spark.createDataFrame(data, columns)
        
        # Show the DataFrame
        print("DataFrame created successfully:")
        df.show()
        
        # Get Spark context info
        sc = spark.sparkContext
        print(f"Spark Application ID: {sc.applicationId}")
        print(f"Spark Master: {sc.master}")
        print(f"Spark Version: {sc.version}")
        
        # Stop Spark session
        spark.stop()
        
        return {
            "status": "success",
            "master": "spark://172.20.0.2:7077",
            "version": sc.version,
            "app_id": sc.applicationId
        }
        
    except Exception as e:
        print(f"Error connecting to Spark: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@flow(name="spark-integration-test")
def test_spark_integration_flow():
    """Test Prefect + Spark integration"""
    print("Testing Spark integration from Prefect...")
    
    # Get container info
    hostname = os.environ.get('HOSTNAME', 'unknown')
    print(f"Running on Prefect worker: {hostname}")
    
    # Test Spark connection
    result = test_spark_connection()
    
    print(f"Test result: {result}")
    return result

if __name__ == "__main__":
    test_spark_integration_flow()