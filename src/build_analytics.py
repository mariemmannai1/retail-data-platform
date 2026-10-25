
from pathlib import Path
import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "retail.duckdb"
sql_path = project_dir / "sql" / "build_analytics.sql"

sql_script = sql_path.read_text(encoding="utf-8")

with duckdb.connect(str(db_path)) as con:
    con.execute(sql_script)

    for table in [
        "fact_sales",
        "dim_products",
        "dim_stores",
        "dim_customers",
	"fact_inventory",
    "daily_sales",
    ]:
        count = con.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"{table} : {count} lignes")

print("\nModèle analytique créé avec succès.")
