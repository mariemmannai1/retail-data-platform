
import os
from pathlib import Path

import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent

DB_NAME = os.getenv(
    "RETAIL_DB_NAME",
    "retail_docker_test.duckdb"
)
DB_PATH = PROJECT_DIR / DB_NAME

if not DB_PATH.exists():
    raise SystemExit(f"Base introuvable : {DB_PATH}")

print(f"Base utilisée : {DB_PATH.name}")

with duckdb.connect(str(DB_PATH), read_only=True) as con:
    tables = con.execute("SHOW TABLES").fetchall()

    print("\nTables disponibles :")
    for table in tables:
        print("-", table[0])

    if any(table[0] == "daily_sales" for table in tables):
        print("\nStructure de daily_sales :")
        print(con.execute("DESCRIBE daily_sales").fetchdf())
    else:
        raise ValueError("Table daily_sales introuvable.")

print(f"\nVérification terminée : {DB_NAME}")
