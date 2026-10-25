
import os
from pathlib import Path

import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent

DB_NAME = os.getenv(
    "RETAIL_DB_NAME",
    "retail_docker_test.duckdb"
)
DB_PATH = PROJECT_DIR / DB_NAME

with duckdb.connect(str(DB_PATH), read_only=True) as con:
    checks = {
        "Dates couvertes": """
            SELECT MIN(order_date), MAX(order_date),
                   COUNT(DISTINCT order_date)
            FROM daily_sales
        """,
        "Valeurs manquantes": """
            SELECT
                COUNT(*) FILTER (WHERE order_date IS NULL),
                COUNT(*) FILTER (WHERE order_channel IS NULL),
                COUNT(*) FILTER (WHERE number_of_orders IS NULL),
                COUNT(*) FILTER (WHERE total_revenue IS NULL),
                COUNT(*) FILTER (WHERE average_order_value IS NULL)
            FROM daily_sales
        """,
        "Doublons date + canal": """
            SELECT COUNT(*) FROM (
                SELECT order_date, order_channel
                FROM daily_sales
                GROUP BY order_date, order_channel
                HAVING COUNT(*) > 1
            ) AS duplicates
        """,
        "Valeurs anormales": """
            SELECT COUNT(*) FROM daily_sales
            WHERE number_of_orders <= 0
               OR total_revenue < 0
               OR average_order_value < 0
        """,
        "Panier moyen incohérent": """
            SELECT COUNT(*) FROM daily_sales
            WHERE number_of_orders > 0
              AND ABS(
                  average_order_value
                  - total_revenue / number_of_orders
              ) > 0.02
        """
    }

    print(f"Base utilisée : {DB_NAME}")
    print("\nVALIDATION DE DAILY_SALES")
    print("=" * 40)

    for name, query in checks.items():
        result = con.execute(query).fetchall()
        print(f"\n{name} :")
        print(result)

print(f"\nValidation terminée : {DB_NAME}")
