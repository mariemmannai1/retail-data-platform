import os
import subprocess
import sys
from pathlib import Path

from airflow.sdk import dag, task
import pendulum

PROJECT_DIR = Path("/opt/retail")
PYTHON = sys.executable
ENV = {
    **os.environ,
    "RETAIL_DB_NAME": "retail_docker_test.duckdb",
}

STEPS = [
    ("build_analytics_test.py",),
    ("validate_analytics_test.py",),
    ("check_relationships.py",),
    ("validate_daily_sales_test.py",),
    ("compare_daily_sales_test.py",),
    ("check_database_test.py",),
    ("forecast_sales.py",),
    ("load_forecast_test.py",),
    ("export_for_powerbi_test.py",),
    ("validate_exports.py",),
]


@dag(
    dag_id="retail_data_pipeline",
    description="Orchestration du pipeline Retail Data Platform sur la base de test",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["retail", "duckdb", "portfolio"],
)
def retail_data_pipeline():

    @task
    def run_step(script_name: str) -> str:
        script_path = PROJECT_DIR / "src" / script_name

        if not script_path.exists():
            raise FileNotFoundError(f"Script introuvable : {script_path}")

        result = subprocess.run(
            [PYTHON, str(script_path)],
            cwd=PROJECT_DIR,
            env=ENV,
            check=True,
            text=True,
        )
        return f"OK : {script_name}"

    previous = None

    for (script_name,) in STEPS:
        current = run_step.override(task_id=script_name.removesuffix(".py"))(
            script_name
        )
        if previous is not None:
            previous >> current
        previous = current


retail_data_pipeline()
