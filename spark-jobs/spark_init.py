"""
Simple Spark initialization module
Provides basic utilities for all Spark jobs
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session(app_name: str, master: str = None) -> SparkSession:
    """Create a basic Spark session with dynamic allocation"""
    
    builder = SparkSession.builder.appName(app_name)
    
    # Set master if provided
    if master:
        builder = builder.master(master)
    
    # Enable dynamic allocation (let Spark manage resources)
    builder = builder.config("spark.dynamicAllocation.enabled", "true")
    builder = builder.config("spark.sql.adaptive.enabled", "true")
    
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    
    logger.info(f"✅ Spark session created: {app_name}")
    logger.info(f"📊 Spark version: {spark.version}")
    logger.info(f"🎯 Master: {spark.sparkContext.master}")
    logger.info(f"🆔 Application ID: {spark.sparkContext.applicationId}")
    
    return spark

def setup_minio_config(spark: SparkSession):
    """Configure Spark for MinIO S3 access"""
    spark.conf.set("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
    spark.conf.set("spark.hadoop.fs.s3a.access.key", "minio")
    spark.conf.set("spark.hadoop.fs.s3a.secret.key", "123456789")
    spark.conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
    spark.conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    spark.conf.set("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    
    logger.info("✅ MinIO S3 configuration applied")

def stop_spark_session(spark: SparkSession):
    """Stop Spark session"""
    if spark:
        spark.stop()
        logger.info("🛑 Spark session stopped")