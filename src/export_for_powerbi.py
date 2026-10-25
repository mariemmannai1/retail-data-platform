
from pathlib import Path

import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "retail.duckdb"
OUTPUT_DIR = PROJECT_DIR / "data" / "powerbi"

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

con = duckdb.connect(str(DB_PATH), read_only=True)

try:
    existing_tables = {
        row[0]
        for row in con.execute("SHOW TABLES").fetchall()
    }

    for table in tables:
        if table not in existing_tables:
            raise ValueError(f"Table introuvable : {table}")

        output_file = OUTPUT_DIR / f"{table}.parquet"
        output_sql_path = str(output_file).replace("\\", "/")

        con.execute(
            f"COPY {table} TO '{output_sql_path}' "
            "(FORMAT PARQUET)"
        )

        rows = con.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"OK | {table} | {rows} lignes | {output_file}")

    print("\nExport Power BI terminé avec succès.")

finally:
    con.close()
