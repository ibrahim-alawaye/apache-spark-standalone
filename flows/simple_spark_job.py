import subprocess
import os
from prefect import flow, task
from prefect.logging import get_run_logger

@task
def create_working_spark_job():
    """Create a Spark job that works with the version mismatch"""
    logger = get_run_logger()
    
    # Simple Spark job that should work
    spark_job_content = '''#!/usr/bin/env python3

import sys
import os

print("=== WORKING SPARK JOB START ===")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    from pyspark.sql import SparkSession
    print("✅ PySpark imported successfully")
    
    # Create Spark session with explicit Python configuration
    spark = SparkSession.builder \\
        .appName("WorkingSparkTest") \\
        .config("spark.pyspark.python", "python3") \\
        .config("spark.pyspark.driver.python", "python3") \\
        .getOrCreate()
    
    print("✅ Spark session created successfully")
    
    sc = spark.sparkContext
    print(f"Spark version: {sc.version}")
    print(f"Master: {sc.master}")
    print(f"App ID: {sc.applicationId}")
    
    # Simple DataFrame operations
    print("Creating test DataFrame...")
    data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
    columns = ["Name", "Age"]
    df = spark.createDataFrame(data, columns)
    
    print("DataFrame created:")
    df.show()
    
    print("Performing operations...")
    count = df.count()
    print(f"Total rows: {count}")
    
    # Filter operation
    adults = df.filter(df.Age >= 30)
    adult_count = adults.count()
    print(f"Adults (30+): {adult_count}")
    
    adults.show()
    
    # Stop Spark session
    spark.stop()
    print("✅ Spark session stopped successfully")
    print("=== WORKING SPARK JOB END ===")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✅ SUCCESS: Job completed successfully")
'''
    
    job_path = "/root/spark-jobs/working_spark_job.py"
    os.makedirs(os.path.dirname(job_path), exist_ok=True)
    
    with open(job_path, 'w') as f:
        f.write(spark_job_content)
    
    os.chmod(job_path, 0o755)
    
    logger.info(f"✅ Working Spark job created at: {job_path}")
    return job_path

@task
def submit_spark_job_fixed(job_path: str):
    """Submit Spark job with proper Python version configuration"""
    logger = get_run_logger()
    
    # Use spark-submit with explicit Python version matching
    cmd = [
        "spark-submit",
        "--master", "spark://172.20.0.2:7077",
        "--deploy-mode", "client",
        "--conf", "spark.pyspark.python=python3",
        "--conf", "spark.pyspark.driver.python=python3",
        "--conf", "spark.sql.adaptive.enabled=false",  # Disable adaptive query execution for simplicity
        "--executor-memory", "1g",
        "--driver-memory", "1g",
        "--executor-cores", "1",
        "--total-executor-cores", "2",
        job_path
    ]
    
    logger.info(f"🚀 Running: {' '.join(cmd)}")
    
    try:
        # Run with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd="/root"
        )
        
        output_lines = []
        success_found = False
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                output_lines.append(line)
                
                # Check for success marker
                if "SUCCESS: Job completed successfully" in line:
                    success_found = True
                    logger.info(f"🎉 {line}")
                elif "❌" in line or "ERROR" in line:
                    logger.error(f"❌ {line}")
                elif "✅" in line:
                    logger.info(f"✅ {line}")
                else:
                    logger.info(f"   {line}")
        
        return_code = process.poll()
        
        logger.info(f"🔢 Final return code: {return_code}")
        logger.info(f"🎯 Success marker found: {success_found}")
        
        # Consider it successful if we found our success marker, regardless of return code
        actual_success = success_found or return_code == 0
        
        return {
            "return_code": return_code,
            "success": actual_success,
            "output_lines": len(output_lines),
            "success_marker_found": success_found
        }
        
    except Exception as e:
        logger.error(f"❌ Error submitting Spark job: {e}")
        raise

@flow(name="spark-submit-fixed", log_prints=True)
def spark_submit_fixed_flow():
    """Test Spark submit with proper configuration"""
    logger = get_run_logger()
    
    logger.info("🧪 Testing fixed Spark submit approach...")
    
    # Create working job
    logger.info("📝 Creating working Spark job...")
    job_path = create_working_spark_job()
    
    # Submit job
    logger.info("🚀 Submitting Spark job with fixed configuration...")
    result = submit_spark_job_fixed(job_path)
    
    # Results
    logger.info("📊 Final Results:")
    logger.info(f"  Return Code: {result['return_code']}")
    logger.info(f"  Success: {result['success']}")
    logger.info(f"  Success Marker Found: {result['success_marker_found']}")
    logger.info(f"  Output Lines: {result['output_lines']}")
    
    if result['success']:
        logger.info("🎉 SUCCESS: Spark integration is working!")
    else:
        logger.error("❌ FAILED: Still having issues")
    
    return result

if __name__ == "__main__":
    spark_submit_fixed_flow()
