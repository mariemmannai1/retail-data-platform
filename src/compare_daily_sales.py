
import sys
from pathlib import Path

import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "retail.duckdb"

with duckdb.connect(str(DB_PATH), read_only=True) as con:
    source_sales = """
        SELECT
            CAST(order_datetime AS DATE) AS order_date,
            order_channel,
            COUNT(*) AS number_of_orders,
            ROUND(SUM(total_amount), 2) AS total_revenue,
            ROUND(
                SUM(total_amount) / NULLIF(COUNT(*), 0),
                2
            ) AS average_order_value
        FROM read_csv_auto('data/raw/orders.csv')
        WHERE order_status = 'Completed'
        GROUP BY 1, 2
    """

    # 1. Comparer les données sources avec daily_sales
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

    # 2. Afficher les différences de panier moyen
    details = con.execute(f"""
        WITH source_sales AS ({source_sales})
        SELECT
            s.order_date,
            s.order_channel,
            s.average_order_value AS source_aov,
            d.average_order_value AS model_aov,
            s.average_order_value - d.average_order_value AS difference
        FROM source_sales s
        JOIN daily_sales d
            ON s.order_date = d.order_date
            AND s.order_channel = d.order_channel
            WHERE ABS(
                s.average_order_value - d.average_order_value
            ) > 0.010001
        ORDER BY ABS(
            s.average_order_value - d.average_order_value
        ) DESC
    """).fetchdf()

    print("\nDETAIL DES DIFFERENCES DE PANIER MOYEN")
    print(
        details.to_string(index=False)
        if not details.empty
        else "Aucune différence."
    )

    # 3. Diagnostic du groupe précédemment identifié
    detail_source = con.execute("""
        SELECT
            COUNT(*) AS orders,
            SUM(total_amount) AS revenue_exact,
            AVG(total_amount) AS aov_exact,
            ROUND(AVG(total_amount), 2) AS aov_rounded
        FROM read_csv_auto('data/raw/orders.csv')
        WHERE order_status = 'Completed'
          AND CAST(order_datetime AS DATE) = DATE '2025-03-20'
          AND order_channel = 'Online'
    """).fetchdf()

    print("\nDETAIL SOURCE SANS ARRONDI")
    print(detail_source.to_string(index=False))

    detail_model = con.execute("""
        SELECT
            COUNT(*) AS orders,
            SUM(total_amount) AS revenue_exact,
            AVG(total_amount) AS aov_exact,
            ROUND(AVG(total_amount), 2) AS aov_rounded
        FROM fact_orders
        WHERE order_status = 'Completed'
          AND order_date = DATE '2025-03-20'
          AND order_channel = 'Online'
    """).fetchdf()

    print("\nDETAIL FACT_ORDERS SANS ARRONDI")
    print(detail_model.to_string(index=False))

    # 4. Arrêter la pipeline si les contrôles échouent
    if any(value != 0 for value in differences):
        print("\nECHEC : les données sources et daily_sales divergent.")
        sys.exit(1)

    print("\nSUCCES : toutes les comparaisons sont conformes.")
