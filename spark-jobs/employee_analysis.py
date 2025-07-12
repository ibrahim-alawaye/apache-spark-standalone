"""
Simple employee data analysis Spark job
Pure Spark job - no Prefect dependencies
"""

import sys
import os
from spark_init import create_spark_session, stop_spark_session
from pyspark.sql.functions import col, avg, count, when

def main():
    """Main job function"""
    spark = None
    
    try:
        print("🚀 Starting Employee Analysis Job...")
        
        # Create Spark session
        spark = create_spark_session("EmployeeAnalysisJob")
        
        # Create sample employee data
        print("📊 Creating employee dataset...")
        data = [
            ("John Doe", 28, 75000, "Engineering", "Full-time"),
            ("Jane Smith", 32, 85000, "Engineering", "Full-time"),
            ("Bob Johnson", 45, 95000, "Engineering", "Full-time"),
            ("Alice Brown", 29, 65000, "Marketing", "Full-time"),
            ("Charlie Wilson", 35, 70000, "Marketing", "Part-time"),
            ("Diana Davis", 41, 90000, "Sales", "Full-time"),
            ("Eve Miller", 26, 60000, "Sales", "Contract"),
            ("Frank Garcia", 38, 80000, "HR", "Full-time"),
            ("Grace Lee", 33, 72000, "HR", "Full-time"),
            ("Henry Taylor", 42, 88000, "Finance", "Full-time")
        ]
        
        columns = ["name", "age", "salary", "department", "employment_type"]
        df = spark.createDataFrame(data, columns)
        
        print("📋 Employee Data:")
        df.show()
        
        # Analysis 1: Department statistics
        print("🏢 Department Analysis:")
        dept_stats = df.groupBy("department").agg(
            count("*").alias("employee_count"),
            avg("age").alias("avg_age"),
            avg("salary").alias("avg_salary")
        ).orderBy(col("employee_count").desc())
        
        dept_stats.show()
        
        # Analysis 2: Age groups
        print("👥 Age Group Analysis:")
        age_groups = df.withColumn(
            "age_group",
            when(col("age") < 30, "Young")
            .when(col("age") < 40, "Middle")
            .otherwise("Senior")
        ).groupBy("age_group").agg(
            count("*").alias("count"),
            avg("salary").alias("avg_salary")
        ).orderBy("age_group")
        
        age_groups.show()
        
        # Analysis 3: Employment type breakdown
        print("💼 Employment Type Analysis:")
        employment_stats = df.groupBy("employment_type").agg(
            count("*").alias("count"),
            avg("salary").alias("avg_salary")
        ).orderBy(col("count").desc())
        
        employment_stats.show()
        
        # Summary statistics
        total_employees = df.count()
        avg_salary = df.agg(avg("salary")).collect()[0][0]
        avg_age = df.agg(avg("age")).collect()[0][0]
        
        print("📊 Summary Statistics:")
        print(f"   Total Employees: {total_employees}")
        print(f"   Average Salary: ${avg_salary:,.2f}")
        print(f"   Average Age: {avg_age:.1f} years")
        
        print("✅ SUCCESS: Employee Analysis Job completed!")
        
        return {
            "status": "success",
            "total_employees": total_employees,
            "avg_salary": avg_salary,
            "avg_age": avg_age
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}
        
    finally:
        if spark:
            stop_spark_session(spark)

if __name__ == "__main__":
    result = main()
    print(f"🎯 Final Result: {result}")
    
    # Exit with appropriate code
    if result.get("status") == "success":
        sys.exit(0)
    else:
        sys.exit(1)