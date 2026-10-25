"""Tests de dim_date et fact_orders (étape 4)."""
from conftest import scalar


# ---------- dim_date ----------
def test_dim_date_covers_every_day_of_2025(con):
    first, last, rows = con.execute(
        "SELECT MIN(date_key), MAX(date_key), COUNT(*) FROM dim_date").fetchone()
    assert (str(first), str(last), rows) == ("2025-01-01", "2025-12-31", 365)


def test_dim_date_key_is_unique_and_continuous(con):
    assert scalar(con, "SELECT COUNT(*) - COUNT(DISTINCT date_key) FROM dim_date") == 0
    assert scalar(con, "SELECT COUNT(*) FROM (SELECT date_key - LAG(date_key) OVER (ORDER BY date_key) AS gap "
                       "FROM dim_date) WHERE gap IS NOT NULL AND gap <> 1") == 0


def test_every_sale_date_exists_in_dim_date(con):
    for table, column in [("fact_sales", "order_date"), ("fact_orders", "order_date"),
                          ("daily_sales", "order_date")]:
        missing = scalar(con, f"""
            SELECT COUNT(*) FROM {table} t LEFT JOIN dim_date d ON t.{column} = d.date_key
            WHERE d.date_key IS NULL""")
        assert missing == 0, f"{table}.{column} contient des dates absentes de dim_date"


# ---------- fact_orders ----------
def test_fact_orders_one_row_per_order(con):
    assert scalar(con, "SELECT COUNT(*) FROM fact_orders") == 10000
    assert scalar(con, "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM fact_orders") == 0


def test_fact_orders_matches_fact_sales(con):
    # chaque commande de fact_orders a le même nombre de lignes, de quantités et de ventes nettes
    mismatches = scalar(con, """
        SELECT COUNT(*) FROM fact_orders o
        JOIN (SELECT order_id, COUNT(*) AS lines, SUM(quantity) AS units, ROUND(SUM(line_net_amount), 2) AS net
              FROM fact_sales GROUP BY 1) s USING (order_id)
        WHERE o.line_count <> s.lines OR o.units <> s.units OR ABS(o.net_sales - s.net) > 0.011""")
    assert mismatches == 0
    assert scalar(con, "SELECT COUNT(*) FROM fact_orders WHERE line_count = 0") == 0


def test_fact_orders_official_kpis(con):
    orders, revenue, net_sales, units = con.execute("""
        SELECT COUNT(*), ROUND(SUM(total_amount), 2), ROUND(SUM(net_sales), 2), SUM(units)
        FROM fact_orders WHERE order_status = 'Completed'""").fetchone()
    assert (orders, revenue, net_sales, units) == (9589, 249520.30, 228457.01, 90585)
