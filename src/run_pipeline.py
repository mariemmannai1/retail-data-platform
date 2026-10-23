
from pathlib import Path
import subprocess
import sys

PROJECT_DIR = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
WITH_FORECAST = "--with-forecast" in sys.argv

STEPS = [
    ("Construction du modele analytique", "build_analytics.py"),
    ("Validation du modele et des stocks", "validate_analytics.py"),
    ("Validation des relations", "check_relationships.py"),
    ("Validation de daily_sales", "validate_daily_sales.py"),
    ("Comparaison de daily_sales", "compare_daily_sales.py"),
    ("Verification de la base", "check_database.py"),
]

if WITH_FORECAST:
    STEPS.append(
        ("Generation des previsions IA", "forecast_sales.py")
    )

STEPS.extend([
    ("Chargement des previsions et metriques", "load_forecast.py"),
    ("Export des tables pour Power BI", "export_for_powerbi.py"),
])

print("=" * 55)
print("RETAIL DATA PLATFORM - PIPELINE")
print("=" * 55)

for description, script in STEPS:
    script_path = PROJECT_DIR / "src" / script

    print(f"\n\nETAPE : {description}")
    print("-" * 55)

    if not script_path.exists():
        print(f"ERREUR : script introuvable : {script_path}")
        sys.exit(1)

    result = subprocess.run(
        [PYTHON, str(script_path)],
        cwd=PROJECT_DIR,
        check=False,
    )

    if result.returncode != 0:
        print(f"\nECHEC : {script}")
        print("La pipeline est arretee.")
        sys.exit(result.returncode)

print("\n" + "=" * 55)
print("PIPELINE TERMINEE AVEC SUCCES")
print("=" * 55)
