
from pathlib import Path

import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "retail.duckdb"

csv_files = [
    "orders.csv",
    "order_items.csv",
    "products.csv",
    "customers.csv",
    "stores.csv",
    "inventory.csv",
]

with duckdb.connect(str(db_path), read_only=True) as con:
    for filename in csv_files:
        csv_path = project_dir / "data" / "raw" / filename

        print(f"\n{'=' * 50}")
        print(f"Fichier : {filename}")

        if not csv_path.exists():
            print("Fichier introuvable.")
            continue

        escaped_path = str(csv_path).replace("\\", "/").replace("'", "''")

        result = con.execute(
            f"DESCRIBE SELECT * FROM read_csv_auto('{escaped_path}')"
        ).fetchdf()

        print(result[["column_name", "column_type"]].to_string(index=False))
