"""
Simple Spark Job Submitter
Just submit any Spark job easily!
"""

import subprocess
import os
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SparkRunner:
    def __init__(self):
        self.spark_host = os.getenv('SPARK_HOST', '172.20.0.2')
        self.spark_user = os.getenv('SPARK_USER', 'root')
        self.spark_pass = os.getenv('SPARK_PASS', 'sparkpass')
        
    def copy_file_to_spark(self, local_file: str, remote_path: str = "/root/spark-jobs/") -> bool:
        """Copy a local file to Spark master."""
        try:
            remote_file = os.path.join(remote_path, os.path.basename(local_file))
            cmd = [
                'sshpass', '-p', self.spark_pass, 'scp',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'LogLevel=ERROR',
                local_file, f'{self.spark_user}@{self.spark_host}:{remote_file}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"File copied: {local_file} -> {remote_file}")
                return True
            else:
                logger.error(f"File copy failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Copy error: {e}")
            return False
    
    def run_ssh_command(self, command: str, timeout: int = 60) -> tuple[bool, str]:
        """Run a command on Spark master via SSH."""
        try:
            ssh_cmd = [
                'sshpass', '-p', self.spark_pass, 'ssh',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'LogLevel=ERROR',
                f'{self.spark_user}@{self.spark_host}',
                command
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except Exception as e:
            logger.error(f"SSH command error: {e}")
            return False, str(e)
    
    def submit_job(self, job_file: str, main_class: str = None, app_args: list = None, spark_args: dict = None) -> bool:
        """Submit a Spark job with full logging."""
        try:
            cmd_parts = [
                "/opt/spark/bin/spark-submit",
                "--master", "spark://spark-master:7077",
                "--deploy-mode", "client"
            ]
            
            if spark_args:
                for key, value in spark_args.items():
                    cmd_parts.extend([f"--{key}", str(value)])
            
            if main_class:
                cmd_parts.extend(["--class", main_class])
            
            cmd_parts.append(job_file)
            
            if app_args:
                cmd_parts.extend([str(arg) for arg in app_args])
            
            spark_cmd = " ".join(cmd_parts)
            
            logger.info(f"🚀 Submitting: {spark_cmd}")
            print("=" * 80)
            print("SPARK JOB EXECUTION LOGS:")
            print("=" * 80)
            
            ssh_cmd = [
                'sshpass', '-p', self.spark_pass, 'ssh',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'LogLevel=ERROR',
                f'{self.spark_user}@{self.spark_host}',
                f'source /root/.bashrc && {spark_cmd}'
            ]
            
            # Use Popen for real-time output
            process = subprocess.Popen(
                ssh_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Print output in real-time
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    output_lines.append(output.strip())
                    sys.stdout.flush()
            
            return_code = process.poll()
            
            print("=" * 80)
            if return_code == 0:
                logger.info("Job completed successfully")
                return True
            else:
                logger.error(f"Job failed with return code: {return_code}")
                return False
                
        except Exception as e:
            logger.error(f"Submission error: {e}")
            return False
    
    def submit_python_job(self, python_file: str, app_args: list = None, spark_args: dict = None) -> bool:
        """Submit a Python Spark job."""
        return self.submit_job(python_file, app_args=app_args, spark_args=spark_args)
    
    def submit_jar_job(self, jar_file: str, main_class: str, app_args: list = None, spark_args: dict = None) -> bool:
        """Submit a JAR Spark job."""
        return self.submit_job(jar_file, main_class=main_class, app_args=app_args, spark_args=spark_args)
    
    def copy_and_submit_python_job(self, local_python_file: str, spark_args: dict = None) -> bool:
        """Copy Python file to Spark master and submit it."""
        if not self.copy_file_to_spark(local_python_file):
            return False
        
        remote_file = f"/root/spark-jobs/{os.path.basename(local_python_file)}"
        return self.submit_python_job(remote_file, spark_args=spark_args)
    
    def verify_output(self, output_path: str = "/tmp/output/") -> bool:
        """Verify output files exist."""
        success, output = self.run_ssh_command(f"ls -la {output_path}")
        if success:
            print("Output verification:")
            print(output)
            return True
        else:
            logger.error(f"Output verification failed: {output}")
            return False
    
    def test_connection(self) -> bool:
        """Test connection."""
        try:
            result = subprocess.run(["/opt/prefect/spark-ssh.sh", "test"], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except:
            return False

# Global instance
spark = SparkRunner()

# Simple functions
def copy_file_to_spark(local_file: str, remote_path: str = "/root/spark-jobs/") -> bool:
    """Copy file to Spark master."""
    return spark.copy_file_to_spark(local_file, remote_path)

def run_ssh_command(command: str, timeout: int = 60) -> tuple[bool, str]:
    """Run SSH command on Spark master."""
    return spark.run_ssh_command(command, timeout)

def submit_spark_job(job_file: str, main_class: str = None, app_args: list = None, spark_args: dict = None) -> bool:
    """Submit any Spark job."""
    return spark.submit_job(job_file, main_class, app_args, spark_args)

def submit_python_job(python_file: str, app_args: list = None, spark_args: dict = None) -> bool:
    """Submit Python job."""
    return spark.submit_python_job(python_file, app_args, spark_args)

def submit_jar_job(jar_file: str, main_class: str, app_args: list = None, spark_args: dict = None) -> bool:
    """Submit JAR job."""
    return spark.submit_jar_job(jar_file, main_class, app_args, spark_args)

def copy_and_submit_python_job(local_python_file: str, spark_args: dict = None) -> bool:
    """Copy and submit Python job in one step."""
    return spark.copy_and_submit_python_job(local_python_file, spark_args)

def verify_output(output_path: str = "/tmp/output/") -> bool:
    """Verify output files."""
    return spark.verify_output(output_path)

def test_spark() -> bool:
    """Test Spark connection."""
    return spark.test_connection()

if __name__ == "__main__":
    print("Testing Spark job submission...")
    
    if not test_spark():
        print("Connection failed!")
        exit(1)
    
    print("Connection OK")
    
    print("Testing Spark Pi...")
    success = submit_jar_job(
        jar_file="/opt/spark/examples/jars/spark-examples_2.12-3.5.0.jar",
        main_class="org.apache.spark.examples.SparkPi",
        app_args=["3"],
        spark_args={"executor-memory": "512m", "driver-memory": "512m"}
    )
    
    if success:
        print("Test successful!")
    else:
        print("Test failed!")
