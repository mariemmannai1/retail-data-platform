
FROM apache/airflow:3.1.0

USER airflow

COPY airflow/constraints-3.12.txt /tmp/constraints.txt
COPY airflow/requirements.txt /tmp/airflow-requirements.txt

RUN pip install --no-cache-dir \
    --constraint /tmp/constraints.txt \
    -r /tmp/airflow-requirements.txt
