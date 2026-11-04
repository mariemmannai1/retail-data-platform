
import os
from pathlib import Path

import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_FILE = PROJECT_DIR / os.getenv("RETAIL_DB_NAME", "retail.duckdb")
PARQUET_DIR = PROJECT_DIR / "data" / "spark_daily_orders"

con = duckdb.connect(str(DB_FILE), read_only=True)

try:
    parquet_path = str(PARQUET_DIR / "*.parquet")

    spark_count = con.execute(
        "SELECT COUNT(*) FROM read_parquet(?)",
        [parquet_path],
    ).fetchone()[0]

    sql_count = con.execute(
        "SELECT COUNT(*) FROM daily_sales"
    ).fetchone()[0]

    spark_total = con.execute(
        "SELECT SUM(total_revenue) FROM read_parquet(?)",
        [parquet_path],
    ).fetchone()[0]

    sql_total = con.execute(
        "SELECT SUM(total_revenue) FROM daily_sales"
    ).fetchone()[0]

    print(f"Lignes Spark : {spark_count}")
    print(f"Lignes daily_sales : {sql_count}")
    print(f"Revenu total Spark : {spark_total:.2f}")
    print(f"Revenu total daily_sales : {sql_total:.2f}")
    print(f"Écart de revenu : {abs(spark_total - sql_total):.6f}")

    assert spark_count == sql_count, "Le nombre de lignes est différent."
    assert abs(spark_total - sql_total) < 0.01, "Les revenus diffèrent."

    print("VALIDATION RÉUSSIE")

finally:
    con.close()
