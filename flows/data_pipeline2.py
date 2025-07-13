from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sum as spark_sum, avg, count, max as spark_max, min as spark_min,
    when, lit, datediff, current_timestamp, rank, dense_rank, 
    percentile_approx, stddev, lag, lead
)
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
from pyspark.sql.window import Window
import random
from datetime import datetime, timedelta

def generate_sample_data(spark):
    """Generate sample e-commerce data."""
    
    # Sales data with multiple dimensions
    sales_data = []
    products = ["Laptop", "Phone", "Tablet", "Watch", "Headphones"]
    regions = ["North", "South", "East", "West", "Central"]
    channels = ["Online", "Store", "Mobile"]
    
    for i in range(5000):  # 5K records
        sales_data.append((
            f"TXN_{i:05d}",
            random.choice(products),
            random.choice(regions),
            random.choice(channels),
            random.randint(1, 10),  # quantity
            round(random.uniform(100, 2000), 2),  # price
            round(random.uniform(0, 0.3), 2),  # discount
            datetime.now() - timedelta(days=random.randint(0, 365)),
            f"CUST_{random.randint(1, 1000):04d}"
        ))
    
    schema = StructType([
        StructField("transaction_id", StringType(), True),
        StructField("product", StringType(), True),
        StructField("region", StringType(), True),
        StructField("channel", StringType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DoubleType(), True),
        StructField("discount", DoubleType(), True),
        StructField("transaction_date", TimestampType(), True),
        StructField("customer_id", StringType(), True)
    ])
    
    return spark.createDataFrame(sales_data, schema)

def perform_advanced_analytics(df):
    """Perform complex analytics on sales data."""
    
    print("🔍 Performing Advanced Analytics...")
    
    # Calculate revenue and add derived columns
    df_enriched = df.withColumn(
        "revenue", col("quantity") * col("unit_price") * (1 - col("discount"))
    ).withColumn(
        "profit_margin", when(col("unit_price") > 500, 0.3).otherwise(0.2)
    ).withColumn(
        "profit", col("revenue") * col("profit_margin")
    )
    
    # 1. Product Performance Analysis
    product_analysis = df_enriched.groupBy("product") \
        .agg(
            spark_sum("revenue").alias("total_revenue"),
            spark_sum("profit").alias("total_profit"),
            count("transaction_id").alias("total_transactions"),
            avg("unit_price").alias("avg_price"),
            stddev("revenue").alias("revenue_volatility"),
            percentile_approx("revenue", 0.5).alias("median_revenue")
        )
    
    # Add product rankings
    product_window = Window.orderBy(col("total_revenue").desc())
    product_analysis = product_analysis.withColumn(
        "revenue_rank", rank().over(product_window)
    ).withColumn(
        "performance_tier",
        when(col("revenue_rank") <= 2, "Top Performer")
        .when(col("revenue_rank") <= 4, "Good Performer")
        .otherwise("Average Performer")
    )
    
    # 2. Regional Performance with Growth Analysis
    regional_monthly = df_enriched \
        .withColumn("year_month", col("transaction_date").cast("date")) \
        .groupBy("region", "year_month") \
        .agg(spark_sum("revenue").alias("monthly_revenue"))
    
    # Calculate month-over-month growth
    regional_window = Window.partitionBy("region").orderBy("year_month")
    regional_growth = regional_monthly.withColumn(
        "prev_month_revenue", lag("monthly_revenue").over(regional_window)
    ).withColumn(
        "growth_rate",
        when(col("prev_month_revenue").isNotNull() & (col("prev_month_revenue") > 0),
             ((col("monthly_revenue") - col("prev_month_revenue")) / col("prev_month_revenue") * 100))
        .otherwise(0)
    )
    
    # 3. Customer Segmentation Analysis
    customer_metrics = df_enriched.groupBy("customer_id") \
        .agg(
            spark_sum("revenue").alias("total_spent"),
            count("transaction_id").alias("transaction_count"),
            avg("revenue").alias("avg_transaction_value"),
            max("transaction_date").alias("last_purchase_date")
        )
    
    # Calculate customer value tiers
    customer_window = Window.orderBy(col("total_spent").desc())
    customer_segments = customer_metrics.withColumn(
        "spending_rank", rank().over(customer_window)
    ).withColumn(
        "customer_tier",
        when(col("spending_rank") <= 100, "VIP")
        .when(col("spending_rank") <= 300, "Premium")
        .when(col("spending_rank") <= 600, "Standard")
        .otherwise("Basic")
    ).withColumn(
        "days_since_last_purchase",
        datediff(current_timestamp(), col("last_purchase_date"))
    )
    
    # 4. Channel Effectiveness Analysis
    channel_analysis = df_enriched.groupBy("channel", "product") \
        .agg(
            spark_sum("revenue").alias("channel_product_revenue"),
            avg("discount").alias("avg_discount"),
            count("transaction_id").alias("transaction_volume")
        )
    
    # Calculate channel efficiency
    channel_totals = df_enriched.groupBy("channel") \
        .agg(spark_sum("revenue").alias("total_channel_revenue"))
    
    channel_efficiency = channel_analysis.join(channel_totals, "channel") \
        .withColumn(
            "revenue_contribution_pct",
            (col("channel_product_revenue") / col("total_channel_revenue") * 100)
        )
    
    return product_analysis, regional_growth, customer_segments, channel_efficiency

def detect_anomalies_and_insights(df):
    """Detect anomalies and generate insights."""
    
    print("🚨 Detecting Anomalies and Generating Insights...")
    
    # Calculate statistical thresholds
    df_with_revenue = df.withColumn(
        "revenue", col("quantity") * col("unit_price") * (1 - col("discount"))
    )
    
    stats = df_with_revenue.agg(
        avg("revenue").alias("mean_revenue"),
        stddev("revenue").alias("stddev_revenue"),
        percentile_approx("revenue", 0.95).alias("p95_revenue")
    ).collect()[0]
    
    # Flag anomalous transactions
    anomalies = df_with_revenue.withColumn(
        "is_high_value",
        when(col("revenue") > stats["p95_revenue"], True).otherwise(False)
    ).withColumn(
        "is_outlier",
        when(col("revenue") > (stats["mean_revenue"] + 2 * stats["stddev_revenue"]), True).otherwise(False)
    ).withColumn(
        "anomaly_score",
        (col("revenue") - stats["mean_revenue"]) / stats["stddev_revenue"]
    )
    
    # Return high-value and outlier transactions
    high_value_transactions = anomalies.filter(
        (col("is_high_value") == True) | (col("is_outlier") == True)
    ).orderBy(col("revenue").desc())
    
    return high_value_transactions

def save_results(product_analysis, regional_growth, customer_segments, channel_efficiency, anomalies):
    """Save results to output directories."""
    
    print("💾 Saving Results...")
    
    # Save each analysis to separate directories
    datasets = [
        (product_analysis, "product_performance"),
        (regional_growth, "regional_growth_analysis"),
        (customer_segments, "customer_segmentation"),
        (channel_efficiency, "channel_effectiveness"),
        (anomalies, "transaction_anomalies")
    ]
    
    for df, name in datasets:
        print(f"Saving {name}...")
        df.coalesce(1).write.mode("overwrite").csv(f"/tmp/output/{name}")
        
        # Show sample results
        print(f"\n📊 Sample {name} results:")
        df.show(5, truncate=False)

def main():
    """Main pipeline execution."""
    
    spark = SparkSession.builder \
        .appName("AdvancedDataPipeline") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    
    try:
        print("Starting Advanced Data Pipeline...")
        
        # Generate sample data
        print("Generating sample data...")
        sales_df = generate_sample_data(spark)
        
        print(f"Generated {sales_df.count()} sales records")
        sales_df.show(5)
        
        # Perform analytics
        product_analysis, regional_growth, customer_segments, channel_efficiency = perform_advanced_analytics(sales_df)
        
        # Detect anomalies
        anomalies = detect_anomalies_and_insights(sales_df)
        
        # Save results
        save_results(product_analysis, regional_growth, customer_segments, channel_efficiency, anomalies)
        
        print("Data Pipeline completed successfully!")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()