import duckdb

con = duckdb.connect("retail.duckdb", read_only=True)

print("EMPLACEMENT DE daily_sales")
print(con.execute("""
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_name = 'daily_sales'
""").fetchall())

print("\nAPERÇU DES 5 PREMIÈRES LIGNES")
print(con.execute("SELECT * FROM daily_sales LIMIT 5").df().to_string(index=False))

con.close()
