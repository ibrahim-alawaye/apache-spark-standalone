
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, max as spark_max

def main():
    spark = SparkSession.builder.appName("DataProcessing").getOrCreate()
    
    print("=== Data Processing Job Started ===")
    
    # Create sample sales data
    sales_data = [
        ("2024-01-01", "Electronics", "Laptop", 1200, "North"),
        ("2024-01-01", "Electronics", "Phone", 800, "South"),
        ("2024-01-02", "Clothing", "Shirt", 50, "North"),
        ("2024-01-02", "Electronics", "Tablet", 400, "East"),
        ("2024-01-03", "Clothing", "Pants", 80, "West"),
        ("2024-01-03", "Electronics", "Laptop", 1300, "South"),
        ("2024-01-04", "Books", "Novel", 25, "North"),
        ("2024-01-04", "Electronics", "Phone", 750, "East"),
    ]
    
    columns = ["date", "category", "product", "amount", "region"]
    df = spark.createDataFrame(sales_data, columns)
    
    print("📊 Sample Sales Data:")
    df.show()
    
    # Analysis 1: Sales by category
    print("📈 Sales by Category:")
    category_sales = df.groupBy("category").agg(
        count("*").alias("total_transactions"),
        avg("amount").alias("avg_amount"),
        spark_max("amount").alias("max_amount")
    ).orderBy(col("total_transactions").desc())
    
    category_sales.show()
    
    # Analysis 2: Sales by region
    print("🌍 Sales by Region:")
    region_sales = df.groupBy("region").agg(
        count("*").alias("transactions"),
        avg("amount").alias("avg_sale")
    ).orderBy(col("avg_sale").desc())
    
    region_sales.show()
    
    # Analysis 3: High-value transactions
    print("💰 High-Value Transactions (>$500):")
    high_value = df.filter(col("amount") > 500)
    high_value.show()
    
    print(f"📊 Total high-value transactions: {high_value.count()}")
    
    spark.stop()
    print("✅ Data Processing Completed!")

if __name__ == "__main__":
    main()

