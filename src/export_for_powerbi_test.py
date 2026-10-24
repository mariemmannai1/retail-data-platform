
from pathlib import Path
import os
import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent

DB_NAME = os.getenv(
    "RETAIL_DB_NAME",
    "retail_docker_test.duckdb"
)
DB_PATH = PROJECT_DIR / DB_NAME

OUTPUT_NAME = os.getenv(
    "RETAIL_EXPORT_DIR",
    "powerbi_docker_test"
)
OUTPUT_DIR = PROJECT_DIR / "data" / OUTPUT_NAME

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tables = [
    "fact_sales",
    "dim_products",
    "dim_customers",
    "dim_stores",
    "fact_inventory",
    "daily_sales",
    "forecast_sales",
    "forecast_model_metrics",
]

with duckdb.connect(str(DB_PATH), read_only=True) as con:
    existing_tables = {
        row[0] for row in con.execute("SHOW TABLES").fetchall()
    }

    for table in tables:
        if table not in existing_tables:
            raise ValueError(f"Table introuvable : {table}")

        output_file = OUTPUT_DIR / f"{table}.parquet"

        # Échapper les apostrophes éventuelles dans le chemin SQL
        output_sql_path = str(output_file.resolve()).replace("\\", "/")
        output_sql_path = output_sql_path.replace("'", "''")

        con.execute(
            f"COPY {table} TO '{output_sql_path}' (FORMAT PARQUET)"
        )

        rows = con.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"OK | {table} | {rows} lignes")

print(f"\nExports terminés : {OUTPUT_DIR}")
