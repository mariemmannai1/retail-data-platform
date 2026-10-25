from pathlib import Path
import duckdb
import sys

db_path = PROJECT_DIR / os.getenv("RETAIL_DB_NAME", "retail_docker_test.duckdb")
folder = PROJECT_DIR / "data" / os.getenv("RETAIL_EXPORT_DIR", "powerbi_docker_test")

with duckdb.connect(str(db_path), read_only=True) as con:
    for table in tables:                      # tables = la liste des 8 noms
        expected_rows = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        actual_rows = con.execute(
            "SELECT COUNT(*) FROM read_parquet(?)", [str(folder / f"{table}.parquet")]
        ).fetchone()[0]
        passed = actual_rows == expected_rows and actual_rows > 0

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
