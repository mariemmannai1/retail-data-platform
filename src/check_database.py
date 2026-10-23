
from pathlib import Path
import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_files = list(project_dir.glob("*.duckdb"))

if not db_files:
    print("Aucune base DuckDB trouvee a la racine du projet.")
    raise SystemExit(1)

db_path = db_files[0]
print(f"Base utilisee : {db_path.name}")

con = duckdb.connect(str(db_path), read_only=True)

tables = con.execute("SHOW TABLES").fetchall()
print("\nTables disponibles :")
for table in tables:
    print("-", table[0])

if any(table[0] == "daily_sales" for table in tables):
    print("\nStructure de daily_sales :")
    print(con.execute("DESCRIBE daily_sales").fetchdf())

    print("\nNombre de lignes :")
    print(con.execute(
        "SELECT COUNT(*) FROM daily_sales"
    ).fetchone()[0])

    print("\nApercu des donnees :")
    print(con.execute(
        "SELECT * FROM daily_sales LIMIT 10"
    ).fetchdf())
else:
    print("\nLa table daily_sales n'existe pas encore.")

con.close()
