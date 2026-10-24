
from pathlib import Path
import os
import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent

DB_NAME = os.getenv(
    "RETAIL_DB_NAME",
    "retail_docker_test.duckdb"
)
DB_PATH = PROJECT_DIR / DB_NAME

CSV_PATH = PROJECT_DIR / "data" / "sales_forecast_7days.csv"
METRICS_PATH = PROJECT_DIR / "data" / "forecast_metrics.csv"

# Vérifier les fichiers nécessaires
for path in [CSV_PATH, METRICS_PATH]:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

with duckdb.connect(str(DB_PATH)) as con:
    # Charger les prévisions
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
        raise ValueError(
            "La table doit contenir exactement 7 prévisions."
        )

    # Charger les métriques du modèle
    con.execute("""
        CREATE OR REPLACE TABLE forecast_model_metrics AS
        SELECT *
        FROM read_csv_auto(?)
    """, [str(METRICS_PATH)])

    print("\nMétriques chargées dans DuckDB :")
    print(con.execute(
        "SELECT * FROM forecast_model_metrics"
    ).fetchdf().to_string(index=False))

print(f"\nChargement terminé : {DB_NAME}")
