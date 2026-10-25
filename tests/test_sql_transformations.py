
import datetime

import duckdb


def test_daily_sales_aggregation():
    con = duckdb.connect(":memory:")

    try:
        con.execute("""
            CREATE TABLE orders (
                order_id VARCHAR,
                order_date DATE,
                order_channel VARCHAR,
                total_amount DOUBLE,
                order_status VARCHAR
            )
        """)

        con.execute("""
            INSERT INTO orders VALUES
                ('O1', '2026-01-01', 'Online', 100, 'Completed'),
                ('O2', '2026-01-01', 'Online', 50, 'Completed'),
                ('O3', '2026-01-01', 'Store', 80, 'Completed'),
                ('O4', '2026-01-01', 'Online', 40, 'Cancelled')
        """)

        result = con.execute("""
            SELECT
                order_date,
                order_channel,
                COUNT(*) AS number_of_orders,
                SUM(total_amount) AS total_revenue,
                AVG(total_amount) AS average_order_value
            FROM orders
            WHERE order_status = 'Completed'
            GROUP BY order_date, order_channel
            ORDER BY order_channel
        """).fetchall()

        expected_date = datetime.date(2026, 1, 1)

        assert result == [
            (expected_date, "Online", 2, 150.0, 75.0),
            (expected_date, "Store", 1, 80.0, 80.0),
        ]

    finally:
        con.close()
