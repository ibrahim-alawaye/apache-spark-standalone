from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("MinIOConnectionTest").getOrCreate()

# Write test
df = spark.range(5)
df.write.mode("overwrite").parquet("s3a://test-bucket/connection-check")

# Read test
df_read = spark.read.parquet("s3a://test-bucket/connection-check")
df_read.show()
