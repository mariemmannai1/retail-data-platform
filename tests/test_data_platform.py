"""Tests de qualité des données et des règles métier (docs/business_rules.md).

Lancer depuis la racine du projet :
    .\\.venv\\Scripts\\python.exe -m pytest tests -v
"""
import pytest
from conftest import scalar


# ---------- Volumétrie ----------
@pytest.mark.parametrize("table, expected", [
    ("fact_sales", 47512), ("dim_products", 66), ("dim_stores", 8),
    ("dim_customers", 800), ("fact_inventory", 528), ("daily_sales", 1061),
])
def test_row_counts(con, table, expected):
    assert scalar(con, f"SELECT COUNT(*) FROM {table}") == expected


def test_fact_sales_has_as_many_rows_as_source(con):
    source = scalar(con, "SELECT COUNT(*) FROM read_csv_auto('data/raw/order_items.csv')")
    assert scalar(con, "SELECT COUNT(*) FROM fact_sales") == source


# ---------- Clés et relations ----------
@pytest.mark.parametrize("table, key", [
    ("fact_sales", "order_item_id"), ("dim_products", "product_id"),
    ("dim_stores", "store_id"), ("dim_customers", "customer_id"),
])
def test_primary_keys_are_unique_and_not_null(con, table, key):
    assert scalar(con, f"SELECT COUNT(*) - COUNT(DISTINCT {key}) FROM {table}") == 0
    assert scalar(con, f"SELECT COUNT(*) FROM {table} WHERE {key} IS NULL") == 0


@pytest.mark.parametrize("child, key, parent", [
    ("fact_sales", "product_id", "dim_products"),
    ("fact_sales", "store_id", "dim_stores"),
    ("fact_sales", "customer_id", "dim_customers"),   # les commandes anonymes (NULL) sont autorisées
    ("fact_inventory", "product_id", "dim_products"),
    ("fact_inventory", "store_id", "dim_stores"),
])
def test_no_orphan_keys(con, child, key, parent):
    orphans = scalar(con, f"""
        SELECT COUNT(*) FROM {child} c LEFT JOIN {parent} p ON c.{key} = p.{key}
        WHERE c.{key} IS NOT NULL AND p.{key} IS NULL""")
    assert orphans == 0


# ---------- Stocks ----------
def test_inventory_has_unique_store_product_pairs(con):
    assert scalar(con, """
        SELECT COUNT(*) FROM (SELECT store_id, product_id FROM fact_inventory
        GROUP BY 1, 2 HAVING COUNT(*) > 1)""") == 0


def test_inventory_has_no_negative_quantities(con):
    assert scalar(con, "SELECT COUNT(*) FROM fact_inventory WHERE stock_on_hand < 0 OR stock_on_order < 0") == 0


def test_inventory_totals(con):
    assert scalar(con, "SELECT SUM(stock_on_hand) FROM fact_inventory") == 91272
    assert scalar(con, "SELECT SUM(stock_on_order) FROM fact_inventory") == 16540


# ---------- daily_sales ----------
def test_daily_sales_covers_every_day_of_2025(con):
    first, last, days = con.execute(
        "SELECT MIN(order_date), MAX(order_date), COUNT(DISTINCT order_date) FROM daily_sales").fetchone()
    assert (str(first), str(last), days) == ("2025-01-01", "2025-12-31", 365)


def test_daily_sales_has_no_duplicate_date_channel(con):
    assert scalar(con, """
        SELECT COUNT(*) FROM (SELECT order_date, order_channel FROM daily_sales
        GROUP BY 1, 2 HAVING COUNT(*) > 1)""") == 0


def test_daily_sales_matches_source_orders(con):
    orders, revenue = con.execute("""
        SELECT COUNT(*), ROUND(SUM(total_amount), 2)
        FROM read_csv_auto('data/raw/orders.csv') WHERE order_status = 'Completed'""").fetchone()
    daily_orders, daily_revenue = con.execute(
        "SELECT SUM(number_of_orders), ROUND(SUM(total_revenue), 2) FROM daily_sales").fetchone()
    assert daily_orders == orders
    assert abs(daily_revenue - revenue) < 0.5


def test_daily_sales_reconciles_with_fact_sales(con):
    # order_total_amount est répété par ligne : on compte une fois par commande
    orders, revenue = con.execute("""
        SELECT COUNT(*), SUM(order_total_amount) FROM (
            SELECT DISTINCT order_id, order_total_amount FROM fact_sales
            WHERE order_status = 'Completed')""").fetchone()
    daily_orders, daily_revenue = con.execute(
        "SELECT SUM(number_of_orders), SUM(total_revenue) FROM daily_sales").fetchone()
    assert daily_orders == orders
    assert abs(daily_revenue - revenue) < 0.5


# ---------- Règles métier (docs/business_rules.md) ----------
def test_official_kpis(con):
    net_sales, quantity, orders = con.execute("""
        SELECT ROUND(SUM(line_net_amount), 2), SUM(quantity), COUNT(DISTINCT order_id)
        FROM fact_sales WHERE order_status = 'Completed'""").fetchone()
    revenue_ttc = scalar(con, "SELECT ROUND(SUM(total_revenue), 2) FROM daily_sales")
    assert net_sales == 228457.01
    assert quantity == 90585
    assert orders == 9589
    assert revenue_ttc == 249520.30
    assert round(revenue_ttc / orders, 2) == 26.02


def test_order_status_counts(con):
    rows = dict(con.execute(
        "SELECT order_status, COUNT(DISTINCT order_id) FROM fact_sales GROUP BY 1").fetchall())
    assert rows == {"Completed": 9589, "Refunded": 225, "Cancelled": 186}


def test_cancelled_orders_have_zero_total(con):
    assert scalar(con, """
        SELECT COUNT(*) FROM (SELECT DISTINCT order_id, order_total_amount FROM fact_sales
        WHERE order_status = 'Cancelled' AND order_total_amount <> 0)""") == 0


def test_line_net_amount_formula(con):
    assert scalar(con, """
        SELECT COUNT(*) FROM fact_sales
        WHERE ABS(line_net_amount - (quantity * unit_price - discount_amount)) > 0.011""") == 0


# ---------- Prévisions (si la table existe) ----------
def test_forecast_table_if_present(con):
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    if "forecast_sales" not in tables:
        pytest.skip("forecast_sales absente : pipeline lancé sans prévision")
    rows = con.execute("SELECT forecast_date, forecast_revenue FROM forecast_sales ORDER BY 1").fetchall()
    assert len(rows) == 7
    assert str(rows[0][0]) == "2026-01-01" and str(rows[-1][0]) == "2026-01-07"
    assert all(value >= 0 for _, value in rows)
