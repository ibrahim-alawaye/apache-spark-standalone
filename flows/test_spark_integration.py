import subprocess
import os
import time
from prefect import flow, task
from prefect.logging import get_run_logger

@task
def create_simple_spark_job():
    """Create a simple Spark job that doesn't rely on PySpark from Prefect"""
    logger = get_run_logger()
    
    # Create a standalone Spark job that handles its own Python environment
    spark_job_content = '''
import sys
import os

def main():
    """Simple Spark job"""
    try:
        print("🚀 Starting Spark job...")
        print(f"🐍 Python version: {sys.version}")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🔧 Python executable: {sys.executable}")
        
        # Import PySpark (this will use whatever Python Spark cluster has)
        from pyspark.sql import SparkSession
        
        # Create Spark session
        spark = SparkSession.builder \\
            .appName("DirectSparkSubmitTest") \\
            .getOrCreate()
        
        print("✅ Spark session created successfully")
        print(f"🎯 Spark Master: {spark.sparkContext.master}")
        print(f"📋 Spark Version: {spark.version}")
        print(f"🔗 Application ID: {spark.sparkContext.applicationId}")
        print(f"🐍 Spark Python: {spark.sparkContext.pythonExec}")
        
        # Create test data
        print("📊 Creating test DataFrame...")
        data = [
            ("Alice", 25, "Engineer", 75000),
            ("Bob", 30, "Manager", 85000), 
            ("Charlie", 35, "Analyst", 65000),
            ("Diana", 28, "Developer", 80000),
            ("Eve", 32, "Designer", 70000)
        ]
        columns = ["Name", "Age", "Role", "Salary"]
        
        df = spark.createDataFrame(data, columns)
        
        print("📋 Original DataFrame:")
        df.show()
        
        # Perform operations to test Spark functionality
        print("🔍 Filtering high earners (Salary > 70000)...")
        high_earners = df.filter(df.Salary > 70000)
        high_earners.show()
        
        print("📈 Statistics:")
        total_count = df.count()
        high_earner_count = high_earners.count()
        avg_salary = df.agg({"Salary": "avg"}).collect()[0][0]
        
        print(f"📊 Total employees: {total_count}")
        print(f"📊 High earners: {high_earner_count}")
        print(f"💰 Average salary: ${avg_salary:,.2f}")
        
        # Group by operations
        print("📊 Average salary by role:")
        df.groupBy("Role").agg({"Salary": "avg", "Age": "avg"}).show()
        
        # More complex operations
        print("🔄 Testing complex operations...")
        from pyspark.sql.functions import col, when, avg
        
        df_with_category = df.withColumn(
            "SalaryCategory",
            when(col("Salary") > 80000, "High")
            .when(col("Salary") > 70000, "Medium")
            .otherwise("Low")
        )
        
        print("📊 Salary categories:")
        df_with_category.groupBy("SalaryCategory").count().show()
        
        # Stop Spark session
        spark.stop()
        print("✅ Spark job completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error in Spark job: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    print(f"🏁 Job finished with exit code: {exit_code}")
    sys.exit(exit_code)
'''
    
    job_path = "/root/spark-jobs/direct_spark_job.py"
    os.makedirs(os.path.dirname(job_path), exist_ok=True)
    
    with open(job_path, 'w') as f:
        f.write(spark_job_content)
    
    logger.info(f"✅ Direct Spark job created at: {job_path}")
    return job_path

@task
def submit_spark_job_direct(job_path: str):
    """Submit Spark job using spark-submit without Python environment conflicts"""
    logger = get_run_logger()
    
    logger.info("🚀 Submitting Spark job directly...")
    
    # Simple spark-submit command - let Spark handle everything
    cmd = [
        "spark-submit",
        "--master", "spark://172.20.0.2:7077",
        "--deploy-mode", "client",
        "--executor-memory", "1g",
        "--driver-memory", "1g",
        "--executor-cores", "1",
        "--total-executor-cores", "2",
        job_path
    ]
    
    logger.info(f"📝 Command: {' '.join(cmd)}")
    
    try:
        start_time = time.time()
        
        # Run spark-submit and capture output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd="/root"
        )
        
        # Stream output in real-time
        output_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                output_lines.append(line)
                logger.info(f"  {line}")
        
        # Wait for process to complete
        return_code = process.poll()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.info(f"⏱️  Execution time: {execution_time:.2f} seconds")
        logger.info(f"🔢 Return code: {return_code}")
        
        if return_code == 0:
            logger.info("✅ Spark job completed successfully")
            return {
                "status": "success",
                "execution_time": execution_time,
                "return_code": return_code,
                "output": output_lines
            }
        else:
            logger.error(f"❌ Spark job failed with return code: {return_code}")
            raise Exception(f"Spark job failed with return code {return_code}")
            
    except Exception as e:
        logger.error(f"❌ Error submitting Spark job: {str(e)}")
        raise

@task
def check_spark_connectivity():
    """Check if we can reach the Spark master"""
    logger = get_run_logger()
    
    try:
        # Test connectivity to Spark master
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://172.20.0.2:8080"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout == "200":
            logger.info("✅ Spark master is reachable")
            return True
        else:
            logger.warning(f"⚠️ Spark master returned HTTP {result.stdout}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Cannot reach Spark master: {str(e)}")
        return False

@flow(name="direct-spark-submit", log_prints=True)
def direct_spark_submit_flow():
    """Submit Spark job directly without Python version conflicts"""
    logger = get_run_logger()
    
    logger.info("🧪 Testing direct Spark submit approach...")
    
    # Check Spark connectivity first
    logger.info("🔍 Checking Spark master connectivity...")
    if not check_spark_connectivity():
        logger.warning("⚠️ Spark master not reachable, but continuing anyway...")
    
    # Create the Spark job
    logger.info("📝 Creating Spark job...")
    job_path = create_simple_spark_job()
    
    # Submit the job
    logger.info("🚀 Submitting Spark job...")
    result = submit_spark_job_direct(job_path)
    
    # Summary
    logger.info("📊 Test Summary:")
    logger.info(f"  Status: {result['status']}")
    logger.info(f"  Execution Time: {result['execution_time']:.2f} seconds")
    logger.info(f"  Return Code: {result['return_code']}")
    logger.info(f"  Output Lines: {len(result['output'])}")
    
    logger.info("🎉 Direct Spark submit test completed!")
    
    return result

if __name__ == "__main__":
    direct_spark_submit_flow()
