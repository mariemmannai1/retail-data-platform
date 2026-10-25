
import os
from pathlib import Path

import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent

DB_NAME = os.getenv(
    "RETAIL_DB_NAME",
    "retail_docker_test.duckdb"
)

db_path = PROJECT_DIR / DB_NAME

with duckdb.connect(str(db_path), read_only=True) as con:
    print("VALIDATION DU MODELE ANALYTIQUE")
    print("=" * 40)

    # 1. Vérifier le nombre de lignes source
    source_count = con.execute("""
        SELECT COUNT(*)
        FROM read_csv_auto('data/raw/order_items.csv')
    """).fetchone()[0]

    fact_count = con.execute("""
        SELECT COUNT(*) FROM fact_sales
    """).fetchone()[0]

    print(f"\nLignes source : {source_count}")
    print(f"Lignes fact_sales : {fact_count}")
    print(f"Nombre de lignes identique : {source_count == fact_count}")

    # 2. Vérifier l'unicité de la clé
    duplicate_count = con.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT order_item_id
            FROM fact_sales
            GROUP BY order_item_id
            HAVING COUNT(*) > 1
        ) d
    """).fetchone()[0]

    print(f"\nClés order_item_id dupliquées : {duplicate_count}")

    # 3. Vérifier les valeurs manquantes
    missing_count = con.execute("""
        SELECT COUNT(*)
        FROM fact_sales
        WHERE order_id IS NULL
           OR product_id IS NULL
           OR order_date IS NULL
           OR order_status IS NULL
    """).fetchone()[0]

    print(f"Enregistrements avec champs essentiels manquants : {missing_count}")

    # 4. Vérifier les statuts
    print("\nRépartition des statuts :")
    print(con.execute("""
        SELECT order_status, COUNT(DISTINCT order_id) AS orders
        FROM fact_sales
        GROUP BY order_status
        ORDER BY orders DESC
    """).fetchdf().to_string(index=False))

    print("\nVALIDATION DES STOCKS")
    print("=" * 40)

    # 5. Vérifier les doublons magasin-produit
    duplicates = con.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT store_id, product_id
            FROM fact_inventory
            GROUP BY store_id, product_id
            HAVING COUNT(*) > 1
        ) d
    """).fetchone()[0]

    print(f"Doublons magasin-produit : {duplicates}")

    # 6. Vérifier les valeurs manquantes
    missing = con.execute("""
        SELECT COUNT(*)
        FROM fact_inventory
        WHERE store_id IS NULL
           OR product_id IS NULL
           OR stock_on_hand IS NULL
           OR stock_on_order IS NULL
    """).fetchone()[0]

    print(f"Enregistrements avec valeurs essentielles manquantes : {missing}")

    # 7. Vérifier les stocks négatifs
    negative = con.execute("""
        SELECT COUNT(*)
        FROM fact_inventory
        WHERE stock_on_hand < 0
           OR stock_on_order < 0
    """).fetchone()[0]

    print(f"Enregistrements avec quantités négatives : {negative}")

    # 8. Résumé des stocks
    print("\nRésumé des stocks :")
    print(con.execute("""
        SELECT
            COUNT(*) AS inventory_records,
            SUM(stock_on_hand) AS total_stock_on_hand,
            SUM(stock_on_order) AS total_stock_on_order,
            COUNT(*) FILTER (WHERE stock_on_hand = 0) AS out_of_stock_records
        FROM fact_inventory
    """).fetchdf().to_string(index=False))

print(f"\nValidation terminée : {DB_NAME}")
