import os
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, countDistinct, sum as spark_sum

PROJECT_DIR = Path(__file__).resolve().parent.parent
ORDERS_FILE = PROJECT_DIR / "data" / "raw" / "orders.csv"
OUTPUT_FILE = PROJECT_DIR / "data" / "spark_daily_orders"


spark = (
    SparkSession.builder
    .appName("Retail-Daily-Orders")
    .config("spark.ui.enabled", "true")
    .config("spark.ui.port", "4040")
    .getOrCreate()
)


spark.sparkContext.setLogLevel("ERROR")

try:
    orders = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(ORDERS_FILE))
    )

    completed = orders.filter(col("order_status") == "Completed")

    daily_sales = (
        completed
        .withColumn("order_date", to_date(col("order_datetime")))
        .groupBy("order_date", "order_channel")
        .agg(
            countDistinct("order_id").alias("number_of_orders"),
            spark_sum("total_amount").alias("total_revenue")
        )
        .orderBy("order_date", "order_channel")
    )

    daily_sales.show(10, truncate=False)

    daily_sales.write.mode("overwrite").parquet(str(OUTPUT_FILE))

    print(f"Nombre de lignes : {daily_sales.count()}")
    print(f"Résultat Parquet : {OUTPUT_FILE}")


finally:
    spark.stop()
