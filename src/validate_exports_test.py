from pathlib import Path
import duckdb
import sys

folder = Path("data/powerbi_docker_test")

expected = {
    "fact_sales": 47512,
    "dim_products": 66,
    "dim_customers": 800,
    "dim_stores": 8,
    "fact_inventory": 528,
    "daily_sales": 1061,
    "forecast_sales": 7,
    "forecast_model_metrics": 1,
}

with duckdb.connect() as con:
    success = True

    for table, expected_rows in expected.items():
        file_path = folder / f"{table}.parquet"

        if not file_path.exists():
            print(f"ERREUR | {table} | fichier absent")
            success = False
            continue

        actual_rows = con.execute(
            "SELECT COUNT(*) FROM read_parquet(?)",
            [str(file_path)]
        ).fetchone()[0]

        passed = actual_rows == expected_rows
        print(
            f"{'OK' if passed else 'ERREUR'} | "
            f"{table} | {actual_rows} lignes"
        )
        success = success and passed

print("\nVALIDATION DES EXPORTS :", "SUCCES" if success else "ECHEC")
sys.exit(0 if success else 1)
