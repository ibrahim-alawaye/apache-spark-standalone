import sys
import subprocess
import time
from minio import Minio
from minio.error import S3Error

from pyspark.sql import SparkSession
import random
from faker import Faker


def validate_minio():
    max_retries = 3
    retry_delay = 5

    client = Minio(
        "minio:9000",
        access_key="minio",
        secret_key="123456789",
        secure=False
    )

    for attempt in range(max_retries):
        try:
            client.list_buckets()
            print("✅ Successfully connected to MinIO")

            bucket_name = "data"
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
                print(f"📦 Created bucket: {bucket_name}")
            else:
                print(f"📦 Bucket already exists: {bucket_name}")
            return True
        except S3Error as e:
            if attempt < max_retries - 1:
                print(f"⚠️ MinIO connection failed. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print("❌ Failed to connect to MinIO after 3 attempts")
                print(f"Error: {e}")
                sys.exit(1)


def create_spark_session():
    return SparkSession.builder \
        .appName("DataGenerator") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minio") \
        .config("spark.hadoop.fs.s3a.secret.key", "123456789") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .getOrCreate()


def generate_data(spark, rows=10000):
    fake = Faker()
    data = [(
        fake.name(),
        fake.email(),
        fake.address(),
        random.randint(18, 80),
        random.uniform(20000.0, 150000.0),
        fake.date_between(start_date='-5y', end_date='today'),
        fake.company(),
        fake.job(),
        random.choice(['Full-time', 'Part-time', 'Contract']),
        random.randint(0, 20)
    ) for _ in range(rows)]

    df = spark.createDataFrame(data, [
        "name", "email", "address", "age",
        "salary", "hire_date", "company",
        "job_title", "employment_type", "years_experience"
    ])

    return df

def write_to_minio(df):
    try:
        df.repartition(10).write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv("s3a://data/employees")
        print("✅ Data written to MinIO successfully")
    except Exception as e:
        if "Class org.apache.hadoop.fs.s3a.S3AFileSystem not found" in str(e):
            print("❌ S3AFileSystem class not found. Rerunning with required JARs...")
            rerun_with_jars()
        else:
            raise


def rerun_with_jars():
    script_path = sys.argv[0]
    command = [
        "spark-submit",
        "--packages", "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.11.1026",
        script_path
    ]
    print("♻️ Running command with extra JARs:", " ".join(command))
    subprocess.run(command)
    sys.exit(0)


def main():
    validate_minio()
    spark = create_spark_session()
    df = generate_data(spark)
    print(f"📊 Total records: {df.count()}")
    write_to_minio(df)


if __name__ == "__main__":
    main()
