
import os
import subprocess
import sys
from pathlib import Path

import pendulum
from airflow.sdk import dag, task


PROJECT_DIR = Path("/opt/retail")
PYTHON = sys.executable
DBT = "/home/airflow/dbt-venv/bin/dbt"

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
    description="Orchestration du pipeline Retail Data Platform avec DuckDB, dbt et Airflow",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["retail", "duckdb", "dbt", "portfolio"],
)
def retail_data_pipeline():

    @task
    def run_step(script_name: str) -> str:
        script_path = PROJECT_DIR / "src" / script_name

        if not script_path.exists():
            raise FileNotFoundError(
                f"Script introuvable : {script_path}"
            )

        subprocess.run(
            [PYTHON, str(script_path)],
            cwd=PROJECT_DIR,
            env=ENV,
            check=True,
            text=True,
        )

        return f"OK : {script_name}"


    @task
    def run_dbt() -> str:
        project_dir = str(PROJECT_DIR / "retail_dbt")

        dbt_env = os.environ.copy()
        dbt_env.pop("PYTHONPATH", None)
        dbt_env.pop("PYTHONHOME", None)
        dbt_env["RETAIL_DB_NAME"] = "retail_docker_test.duckdb"

        for command in ("run", "test"):
            subprocess.run(
                [
                    DBT,
                    command,
                    "--project-dir", project_dir,
                    "--profiles-dir", project_dir,
                ],
                cwd=PROJECT_DIR,
                env=dbt_env,
                check=True,
                text=True,
            )

        return "OK : dbt run + dbt test"

    previous = None
    dbt_task = None

    for (script_name,) in STEPS:
        current = run_step.override(
            task_id=script_name.removesuffix(".py")
        )(script_name)

        if previous is not None:
            if script_name == "compare_daily_sales_test.py":
                if dbt_task is None:
                    raise RuntimeError(
                        "La tâche dbt doit être créée avant la comparaison."
                    )
                previous >> dbt_task >> current
            else:
                previous >> current

        previous = current

        if script_name == "validate_daily_sales_test.py":
            dbt_task = run_dbt()


retail_data_pipeline()
