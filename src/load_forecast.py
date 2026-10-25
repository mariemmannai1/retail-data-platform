
from pathlib import Path

import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "retail.duckdb"
CSV_PATH = PROJECT_DIR / "data" / "sales_forecast_7days.csv"

if not CSV_PATH.exists():
    raise FileNotFoundError(f"Fichier introuvable : {CSV_PATH}")

with duckdb.connect(str(DB_PATH)) as con:
    con.execute("""
        CREATE OR REPLACE TABLE forecast_sales AS
        SELECT
            CAST(date AS DATE) AS forecast_date,
            CAST(forecast_revenue AS DOUBLE) AS forecast_revenue
        FROM read_csv_auto(?)
    """, [str(CSV_PATH)])

    count = con.execute(
        "SELECT COUNT(*) FROM forecast_sales"
    ).fetchone()[0]

    print(f"Lignes chargées : {count}")

    print("\nPrévisions enregistrées dans DuckDB :")
    print(con.execute("""
        SELECT *
        FROM forecast_sales
        ORDER BY forecast_date
    """).fetchdf().to_string(index=False))

    if count != 7:
        raise ValueError("La table doit contenir exactement 7 prévisions.")

print("\nChargement des prévisions terminé.")

# Charger les métriques du modèle dans DuckDB
METRICS_PATH = PROJECT_DIR / "data" / "forecast_metrics.csv"

if not METRICS_PATH.exists():
    raise FileNotFoundError(f"Fichier introuvable : {METRICS_PATH}")

with duckdb.connect(str(DB_PATH)) as con:
    con.execute("""
        CREATE OR REPLACE TABLE forecast_model_metrics AS
        SELECT *
        FROM read_csv_auto(?)
    """, [str(METRICS_PATH)])

    print("\nMétriques chargées dans DuckDB :")
    print(con.execute(
        "SELECT * FROM forecast_model_metrics"
    ).fetchdf().to_string(index=False))