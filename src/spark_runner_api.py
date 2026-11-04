
import os
import subprocess
from fastapi import FastAPI, HTTPException

app = FastAPI()

SPARK_SUBMIT = "/opt/spark/bin/spark-submit"
SPARK_MASTER = "spark://spark:7077"
SCRIPT = "/opt/retail/src/spark_daily_orders.py"

@app.post("/run-spark")
def run_spark():
    try:
        result = subprocess.run(
            [
                SPARK_SUBMIT,
                "--master", SPARK_MASTER,
                SCRIPT,
            ],
            cwd="/opt/retail",
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=result.stderr[-4000:],
            )

        return {
            "status": "success",
            "message": "Spark daily orders terminé",
            "output": result.stdout[-2000:],
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Le traitement Spark a dépassé 10 minutes",
        )
