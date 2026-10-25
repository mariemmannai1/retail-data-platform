from pathlib import Path

import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "retail.duckdb"

with duckdb.connect(str(db_path), read_only=True) as con:
    net_sales, quantity, orders = con.execute("""
        SELECT ROUND(SUM(line_net_amount), 2),
               SUM(quantity),
               COUNT(DISTINCT order_id)
        FROM fact_sales
        WHERE order_status = 'Completed'
    """).fetchone()

    revenue_ttc = con.execute("""
        SELECT ROUND(SUM(total_revenue), 2) FROM daily_sales
    """).fetchone()[0]

    print("KPI OFFICIELS (commandes Completed)")
    print("=" * 40)
    print(f"Net Sales (hors TVA)     : {net_sales}")
    print(f"Revenue TTC              : {revenue_ttc}")
    print(f"Orders                   : {orders}")
    print(f"Quantity                 : {quantity}")
    print(f"Average Order Value      : {round(revenue_ttc / orders, 2)}")