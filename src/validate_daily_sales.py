
from pathlib import Path

import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "retail.duckdb"

with duckdb.connect(str(db_path), read_only=True) as con:
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
        "Panier moyen incoherent": """
            SELECT COUNT(*) FROM daily_sales
            WHERE number_of_orders > 0
              AND ABS(
                  average_order_value
                  - total_revenue / number_of_orders
              ) > 0.02
        """
    }

    print("VALIDATION DE DAILY_SALES")
    print("=" * 40)

    for name, query in checks.items():
        result = con.execute(query).fetchall()
        print(f"\n{name} :")
        print(result)
