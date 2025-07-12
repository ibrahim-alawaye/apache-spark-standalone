import subprocess

# Test 1: Simple local Spark job
print("=== Testing Local Spark ===")
simple_job = '''
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("Test").master("local[1]").getOrCreate()
print("SUCCESS: Spark session created!")
print("Spark version:", spark.version)
spark.stop()
'''

with open("/root/test.py", "w") as f:
    f.write(simple_job)

# Run with spark-submit local
cmd = ["spark-submit", "--master", "local[1]", "/root/test.py"]
print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
print(f"Return code: {result.returncode}")
print("STDOUT:", result.stdout[-500:])  # Last 500 chars
if result.stderr:
    print("STDERR:", result.stderr[-500:])  # Last 500 chars

if result.returncode == 0:
    print("✅ Local test PASSED")
else:
    print("❌ Local test FAILED")
    exit(1)

# Test 2: Check cluster connectivity
print("\n=== Testing Cluster Connectivity ===")
result = subprocess.run(["curl", "-s", "http://172.20.0.2:8080"], capture_output=True, text=True)
if result.returncode == 0:
    print("✅ Spark master is accessible")
    
    # Test 3: Cluster Spark job
    print("\n=== Testing Cluster Spark ===")
    cmd = ["spark-submit", "--master", "spark://172.20.0.2:7077", "/root/test.py"]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    print(f"Return code: {result.returncode}")
    print("STDOUT:", result.stdout[-500:])
    if result.stderr:
        print("STDERR:", result.stderr[-500:])
    
    if result.returncode == 0:
        print("✅ Cluster test PASSED")
    else:
        print("❌ Cluster test FAILED")
else:
    print("❌ Spark master NOT accessible")
