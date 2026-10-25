
from pathlib import Path
import os
import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent

DB_NAME = os.getenv(
    "RETAIL_DB_NAME",
    "retail_docker_test.duckdb"
)

db_path = PROJECT_DIR / DB_NAME
sql_path = PROJECT_DIR / "sql" / "build_analytics.sql"

with duckdb.connect(str(db_path)) as con:
    con.execute(sql_path.read_text(encoding="utf-8"))

    for table in [
        "fact_sales",
        "dim_products",
        "dim_stores",
        "dim_customers",
        "fact_inventory",
    ]:
        count = con.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        print(f"{table} : {count} lignes")

print(f"\nReconstruction terminée : {DB_NAME}")
