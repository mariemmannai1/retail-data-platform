
from pathlib import Path

import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "retail.duckdb"

with duckdb.connect(str(db_path), read_only=True) as con:
    result = con.execute("""
        SELECT
            typeof(MIN(total_amount)) AS amount_type,
            typeof(AVG(total_amount)) AS average_type,
            typeof(ROUND(AVG(total_amount), 2)) AS rounded_type,
            AVG(total_amount) AS average_exact,
            ROUND(AVG(total_amount), 2) AS average_rounded
        FROM fact_orders
        WHERE order_status = 'Completed'
          AND order_date = DATE '2025-03-20'
          AND order_channel = 'Online'
    """).fetchdf()

    print(result.to_string(index=False))
