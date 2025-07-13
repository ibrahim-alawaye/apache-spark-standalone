from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, avg, count

def extract_data(spark):
    sales_data = [
        ("2024-01-01", "Electronics", 1200, "North"),
        ("2024-01-01", "Clothing", 300, "South"),
        ("2024-01-02", "Electronics", 800, "East"),
        ("2024-01-02", "Books", 150, "West"),
        ("2024-01-03", "Clothing", 450, "North"),
        ("2024-01-03", "Electronics", 950, "South"),
        ("2024-01-04", "Books", 200, "East"),
        ("2024-01-04", "Electronics", 1100, "West")
    ]
    
    columns = ["date", "category", "amount", "region"]
    df = spark.createDataFrame(sales_data, columns)
    return df

def transform_data(df):
    category_summary = df.groupBy("category").agg(
        count("*").alias("transaction_count"),
        spark_sum("amount").alias("total_sales"),
        avg("amount").alias("avg_sales")
    )
    
    region_summary = df.groupBy("region").agg(
        count("*").alias("transaction_count"),
        spark_sum("amount").alias("total_sales")
    )
    
    return category_summary, region_summary

def load_data(category_df, region_df):
    category_df.coalesce(1).write.mode("overwrite").csv("/tmp/output/category_summary")
    region_df.coalesce(1).write.mode("overwrite").csv("/tmp/output/region_summary")
    region_df.show()
    print("Data loaded to /tmp/output/")

def main():
    spark = SparkSession.builder.appName("DataPipeline2").getOrCreate()
    
    raw_data = extract_data(spark)
    category_summary, region_summary = transform_data(raw_data)
    load_data(category_summary, region_summary)
    
    print("Pipeline completed successfully")
    spark.stop()

if __name__ == "__main__":
    main()
