from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import logging

# Create a Spark session
logging.getLogger("org.apache.spark.sql").setLevel(logging.ERROR)
spark = SparkSession.builder.appName("MySparkApp").config("spark.master", "local").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# Generate sample data and create a DataFrame
data = [("Alice", 25), ("Bob", 30), ("Charlie", 22), ("David", 28)]
columns = ["name", "age"]
df = spark.createDataFrame(data, columns)

# Show the original data
print("Original Data:")
df.show()

# Perform some transformations (e.g., filter and create a new column)
filtered_df = df.filter(col("age") > 21)
transformed_df = filtered_df.withColumn("age_squared", col("age") ** 2)

# Show the result
print("Transformed Data:")
transformed_df.show()

# Stop the Spark session
spark.stop()
