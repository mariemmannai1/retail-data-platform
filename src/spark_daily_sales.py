
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count
from pyspark.sql.functions import sum as spark_sum

PROJECT_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_DIR / "data" / "sales_forecast_7days.csv"
OUTPUT_DIR = PROJECT_DIR / "data" / "spark_sales_summary"

spark = (
    SparkSession.builder
    .appName("RetailDataPlatform-Sales")
    .master("local[*]")
    .getOrCreate()
)

try:
    df = spark.read.option("header", True).option("inferSchema", True).csv(
        str(INPUT_FILE)
    )

    df.printSchema()
    df.show(5, truncate=False)

    revenue_column = "forecast_revenue"

    if revenue_column not in df.columns:
        raise ValueError(
            f"Colonne '{revenue_column}' absente. Colonnes disponibles : {df.columns}"
        )

    summary = df.agg(
        count("*").alias("number_of_forecast_days"),
        spark_sum(col(revenue_column)).alias("total_predicted_revenue")
    )

    summary.show(truncate=False)

    summary.coalesce(1).write.mode("overwrite").option(
        "header", True
    ).csv(str(OUTPUT_DIR))

    print(f"Résumé Spark exporté dans : {OUTPUT_DIR}")

finally:
    spark.stop()
