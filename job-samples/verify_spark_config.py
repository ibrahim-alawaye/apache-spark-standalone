from pyspark.sql import SparkSession

def verify_spark_config():
    spark = SparkSession.builder \
        .appName("ConfigurationTest") \
        .getOrCreate()

    print("\n=== Spark Configuration Report ===\n")
    
    # Core Configurations
    print("Core Settings:")
    print(f"Master URL: {spark.conf.get('spark.master')}")
    print(f"Driver Memory: {spark.conf.get('spark.driver.memory')}")
    print(f"Executor Memory: {spark.conf.get('spark.executor.memory')}")
    print(f"Executor Cores: {spark.conf.get('spark.executor.cores')}")
    
    # Dynamic Allocation
    print("\nDynamic Allocation:")
    print(f"Enabled: {spark.conf.get('spark.dynamicAllocation.enabled')}")
    print(f"Min Executors: {spark.conf.get('spark.dynamicAllocation.minExecutors')}")
    print(f"Max Executors: {spark.conf.get('spark.dynamicAllocation.maxExecutors')}")
    
    # Memory Management
    print("\nMemory Management:")
    print(f"Storage Fraction: {spark.conf.get('spark.memory.storageFraction')}")
    print(f"Memory Fraction: {spark.conf.get('spark.memory.fraction')}")
    
    # Shuffle Settings
    print("\nShuffle Settings:")
    print(f"Shuffle Partitions: {spark.conf.get('spark.sql.shuffle.partitions')}")
    print(f"Push Enabled: {spark.conf.get('spark.shuffle.push.enabled')}")

if __name__ == "__main__":
    verify_spark_config()