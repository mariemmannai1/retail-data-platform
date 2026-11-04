import duckdb

con = duckdb.connect("retail.duckdb", read_only=True)

print("Nombre de lignes :")
print(con.execute(
    "SELECT COUNT(*) FROM dbt_dev.mart_daily_sales"
).fetchone()[0])

print("\nAperçu :")
print(con.execute("""
    SELECT *
    FROM dbt_dev.mart_daily_sales
    ORDER BY order_date
    LIMIT 5
""").df().to_string(index=False))

print("\nVérification des revenus non positifs :")
print(con.execute("""
    SELECT COUNT(*)
    FROM dbt_dev.mart_daily_sales
    WHERE total_revenue <= 0
""").fetchone()[0])

con.close()