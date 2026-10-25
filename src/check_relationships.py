
import os  # à ajouter avec les imports
from pathlib import Path

import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / os.getenv("RETAIL_DB_NAME", "retail.duckdb")
data_dir = project_dir / "data" / "raw"

with duckdb.connect(str(db_path), read_only=True) as con:
    for filename, key in [
        ("orders.csv", "order_id"),
        ("order_items.csv", "order_item_id"),
        ("products.csv", "product_id"),
        ("customers.csv", "customer_id"),
        ("stores.csv", "store_id"),
    ]:
        path = (data_dir / filename).as_posix()

        query = f"""
            SELECT
                COUNT(*) AS total_rows,
                COUNT({key}) AS non_null_ids,
                COUNT(DISTINCT {key}) AS unique_ids
            FROM read_csv_auto('{path}')
        """

        total, non_null, unique = con.execute(query).fetchone()

        print(f"\n{filename}")
        print(f"Total lignes : {total}")
        print(f"Identifiants non nuls : {non_null}")
        print(f"Identifiants uniques : {unique}")
        print(f"Doublons d'identifiants : {non_null - unique}")
        print(f"Identifiants manquants : {total - non_null}")

    checks = {
        "Commandes sans client correspondant": """
            SELECT COUNT(*)
            FROM read_csv_auto('data/raw/orders.csv') o
            LEFT JOIN read_csv_auto('data/raw/customers.csv') c
                ON o.customer_id = c.customer_id
            WHERE o.customer_id IS NOT NULL
              AND c.customer_id IS NULL
        """,
        "Commandes sans magasin correspondant": """
            SELECT COUNT(*)
            FROM read_csv_auto('data/raw/orders.csv') o
            LEFT JOIN read_csv_auto('data/raw/stores.csv') s
                ON o.store_id = s.store_id
            WHERE o.store_id IS NOT NULL
              AND s.store_id IS NULL
        """,
        "Lignes sans commande correspondante": """
            SELECT COUNT(*)
            FROM read_csv_auto('data/raw/order_items.csv') i
            LEFT JOIN read_csv_auto('data/raw/orders.csv') o
                ON i.order_id = o.order_id
            WHERE o.order_id IS NULL
        """,
        "Lignes sans produit correspondant": """
            SELECT COUNT(*)
            FROM read_csv_auto('data/raw/order_items.csv') i
            LEFT JOIN read_csv_auto('data/raw/products.csv') p
                ON i.product_id = p.product_id
            WHERE p.product_id IS NULL
        """
    }

    print("\nVERIFICATION DES RELATIONS")
    print("=" * 40)

    for name, query in checks.items():
        result = con.execute(query).fetchone()[0]
        print(f"{name} : {result}")
