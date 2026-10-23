
from pathlib import Path
import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "retail.duckdb"

with duckdb.connect(str(db_path), read_only=True) as con:
    print("VERIFICATION DES DONNEES POUR LA PREVISION")
    print("=" * 45)

    print("\nPeriode disponible :")
    print(con.execute("""
        SELECT
            MIN(order_date) AS premiere_date,
            MAX(order_date) AS derniere_date,
            COUNT(DISTINCT order_date) AS nombre_de_jours
        FROM daily_sales
    """).fetchdf().to_string(index=False))

    print("\nVentes quotidiennes totales :")
    print(con.execute("""
        SELECT
            order_date,
            SUM(number_of_orders) AS total_orders,
            ROUND(SUM(total_revenue), 2) AS total_revenue
        FROM daily_sales
        GROUP BY order_date
        ORDER BY order_date
        LIMIT 10
    """).fetchdf().to_string(index=False))

    print("\nNombre de jours sans ventes dans daily_sales :")
    print(con.execute("""
        WITH calendar AS (
            SELECT *
            FROM generate_series(
                (SELECT MIN(order_date) FROM daily_sales),
                (SELECT MAX(order_date) FROM daily_sales),
                INTERVAL 1 DAY
            ) AS t(date)
        )
        SELECT COUNT(*) AS missing_days
        FROM calendar c
        WHERE NOT EXISTS (
            SELECT 1
            FROM daily_sales d
            WHERE d.order_date = CAST(c.date AS DATE)
        )
    """).fetchdf().to_string(index=False))
