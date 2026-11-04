
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/opt/retail")
SPARK_SUBMIT = "/opt/spark/bin/spark-submit"

script = PROJECT_DIR / "src" / "spark_daily_orders.py"

subprocess.run(
    [
        SPARK_SUBMIT,
        "--master", "spark://spark:7077",
        str(script),
    ],
    cwd=PROJECT_DIR,
    check=True,
    text=True,
)

print("Traitement Spark terminé avec succès.")
