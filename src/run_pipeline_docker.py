import os  # Ã  ajouter avec les imports
import subprocess
import sys
from pathlib import Path

ENV = {**os.environ, "RETAIL_DB_NAME": os.getenv("RETAIL_DB_NAME", "retail_docker_test.duckdb")}

PROJECT_DIR = Path(__file__).resolve().parent.parent
PYTHON = sys.executable

STEPS = [
    ("Construction du modÃ¨le analytique", "build_analytics_test.py"),
    ("Validation du modÃ¨le et des stocks", "validate_analytics_test.py"),
    ("Validation des relations", "check_relationships.py"),
    ("Validation de daily_sales", "validate_daily_sales_test.py"),
    ("Comparaison de daily_sales", "compare_daily_sales_test.py"),
    ("VÃ©rification de la base", "check_database_test.py"),
        ("GÃ©nÃ©ration des prÃ©visions IA", "forecast_sales.py"),
    ("Chargement des prÃ©visions IA", "load_forecast_test.py"),
    ("Export des tables Parquet", "export_for_powerbi_test.py"),
    ("Validation des exports Parquet", "validate_exports.py"),
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
        print("Pipeline arrÃªtÃ©e.")
        sys.exit(result.returncode)

print("\n" + "=" * 60)
print("PIPELINE DE TEST TERMINEE AVEC SUCCES")
print("=" * 60)

