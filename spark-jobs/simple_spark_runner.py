"""
Super simple Prefect flow - just runs Spark jobs
"""

import subprocess
from prefect import flow
from prefect.logging import get_run_logger

@flow(name="run-spark-job", log_prints=True)
def run_spark_job(job_name: str):
    """Run a Spark job - that's it!"""
    logger = get_run_logger()
    
    logger.info(f"🚀 Running Spark job: {job_name}")
    
    # Simple command
    cmd = [
        "docker", "exec", "spark-master",
        "/opt/spark/bin/spark-submit",
        "--master", "spark://spark-master:7077",
        f"/root/spark-jobs/{job_name}"
    ]
    
    # Run it
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Show output
    if result.stdout:
        logger.info("Output:")
        logger.info(result.stdout)
    
    if result.stderr:
        logger.info("Errors:")
        logger.info(result.stderr)
    
    # Done
    success = result.returncode == 0
    logger.info(f"✅ Success: {success}")
    
    return success

# Specific job flows
@flow(name="employee-analysis")
def employee_analysis():
    return run_spark_job("employee_analysis.py")

@flow(name="data-generator")
def data_generator():
    return run_spark_job("generate_data.py")

if __name__ == "__main__":
    employee_analysis()