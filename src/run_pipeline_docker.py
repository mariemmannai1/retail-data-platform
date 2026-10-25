from pathlib import Path
import subprocess
import sys
import os   # à ajouter avec les imports

ENV = {**os.environ, "RETAIL_DB_NAME": os.getenv("RETAIL_DB_NAME", "retail_docker_test.duckdb")}

PROJECT_DIR = Path(__file__).resolve().parent.parent
PYTHON = sys.executable

STEPS = [
    ("Construction du modèle analytique", "build_analytics_test.py"),
    ("Validation du modèle et des stocks", "validate_analytics_test.py"),
    ("Validation des relations", "check_relationships.py"),
    ("Validation de daily_sales", "validate_daily_sales_test.py"),
    ("Comparaison de daily_sales", "compare_daily_sales_test.py"),
    ("Vérification de la base", "check_database_test.py"),
        ("Génération des prévisions IA", "forecast_sales.py"),
    ("Chargement des prévisions IA", "load_forecast_test.py"),
    ("Export des tables Parquet", "export_for_powerbi_test.py"),
    ("Validation des exports Parquet", "validate_exports_test.py"),
]


print("=" * 60)
print("RETAIL DATA PLATFORM - PIPELINE DE TEST DOCKER")
print("=" * 60)

for description, script in STEPS:
    script_path = PROJECT_DIR / "src" / script

    print(f"\n\nETAPE : {description}")
    print("-" * 60)

    if not script_path.exists():
        print(f"ERREUR : script introuvable : {script}")
        sys.exit(1)

    result = subprocess.run(
        [PYTHON, str(script_path)],
        cwd=PROJECT_DIR,
        env=ENV,
        check=False,
    )

    if result.returncode != 0:
        print(f"\nECHEC : {script}")
        print("Pipeline arrêtée.")
        sys.exit(result.returncode)

print("\n" + "=" * 60)
print("PIPELINE DE TEST TERMINEE AVEC SUCCES")
print("=" * 60)
