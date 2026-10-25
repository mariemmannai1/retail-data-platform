
from pathlib import Path
import os
import duckdb
import sys

PROJECT_DIR = Path(__file__).resolve().parent.parent

DB_NAME = os.getenv(
    "RETAIL_DB_NAME",
    "retail_docker_test.duckdb"
)

db_path = PROJECT_DIR / DB_NAME

with duckdb.connect(str(db_path), read_only=True) as con:
    source_sales = """
        SELECT
            CAST(order_datetime AS DATE) AS order_date,
            order_channel,
            COUNT(*) AS number_of_orders,
            ROUND(SUM(total_amount), 2) AS total_revenue,
            ROUND(AVG(total_amount), 2) AS average_order_value
        FROM read_csv_auto('data/raw/orders.csv')
        WHERE order_status = 'Completed'
        GROUP BY 1, 2
    """

    # 1. Comparer les groupes et les indicateurs
    differences = con.execute(f"""
        WITH source_sales AS ({source_sales}),
        comparison AS (
            SELECT
                COALESCE(s.order_date, d.order_date) AS order_date,
                COALESCE(s.order_channel, d.order_channel) AS order_channel,
                s.number_of_orders AS source_orders,
                d.number_of_orders AS model_orders,
                s.total_revenue AS source_revenue,
                d.total_revenue AS model_revenue,
                s.average_order_value AS source_aov,
                d.average_order_value AS model_aov
            FROM source_sales s
            FULL OUTER JOIN daily_sales d
                ON s.order_date = d.order_date
                AND s.order_channel = d.order_channel
        )
        SELECT
            COUNT(*) FILTER (
                WHERE source_orders IS NULL OR model_orders IS NULL
            ) AS missing_groups,
            COUNT(*) FILTER (
                WHERE source_orders IS NOT NULL
                  AND model_orders IS NOT NULL
                  AND source_orders != model_orders
            ) AS orders_difference,
            COUNT(*) FILTER (
                WHERE source_revenue IS NOT NULL
                  AND model_revenue IS NOT NULL
                  AND ABS(source_revenue - model_revenue) > 0.01
            ) AS revenue_difference,
            COUNT(*) FILTER (
                WHERE source_aov IS NOT NULL
                  AND model_aov IS NOT NULL
                  AND ABS(source_aov - model_aov) > 0.010001
            ) AS aov_difference
        FROM comparison
    """).fetchone()

    labels = [
        "Groupes manquants",
        "Différences du nombre de commandes",
        "Différences de chiffre d'affaires",
        "Différences de panier moyen",
    ]

    print("\nCONTROLE SOURCE VS DAILY_SALES")
    print("=" * 45)

    for label, value in zip(labels, differences):
        print(f"{label} : {value}")

    # 2. Bloquer la pipeline si une différence existe
    if any(value != 0 for value in differences):
        print("\nECHEC : les données sources et daily_sales divergent.")
        sys.exit(1)

    print("\nSUCCES : toutes les comparaisons sont conformes.")
