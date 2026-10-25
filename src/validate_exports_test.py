from pathlib import Path
import os
import sys

import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent

DB_NAME = os.getenv("RETAIL_DB_NAME", "retail_docker_test.duckdb")
EXPORT_NAME = os.getenv("RETAIL_EXPORT_DIR", "powerbi_docker_test")

db_path = PROJECT_DIR / DB_NAME
folder = PROJECT_DIR / "data" / EXPORT_NAME

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

# Chaque fichier Parquet exporté doit avoir autant de lignes que sa table source.
with duckdb.connect(str(db_path), read_only=True) as con:
    success = True

    for table in tables:
        file_path = folder / f"{table}.parquet"

        if not file_path.exists():
            print(f"ERREUR | {table} | fichier absent")
            success = False
            continue

        expected_rows = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        actual_rows = con.execute(
            "SELECT COUNT(*) FROM read_parquet(?)", [str(file_path)]
        ).fetchone()[0]

        passed = actual_rows == expected_rows and actual_rows > 0
        print(
            f"{'OK' if passed else 'ERREUR'} | {table} | "
            f"{actual_rows} lignes (base : {expected_rows})"
        )
        success = success and passed

print("\nVALIDATION DES EXPORTS :", "SUCCES" if success else "ECHEC")
sys.exit(0 if success else 1)