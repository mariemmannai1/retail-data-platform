
FROM apache/airflow:3.1.0

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow

COPY airflow/constraints-3.12.txt /tmp/constraints.txt
COPY airflow/requirements.txt /tmp/airflow-requirements.txt

RUN pip install --no-cache-dir \
    --constraint /tmp/constraints.txt \
    -r /tmp/airflow-requirements.txt

RUN python -m venv /home/airflow/dbt-venv \
    && /home/airflow/dbt-venv/bin/pip install --no-cache-dir dbt-duckdb==1.11.0 \
    && /home/airflow/dbt-venv/bin/pip install --no-cache-dir protobuf==5.29.5

RUN python -m venv /home/airflow/spark-venv \
    && /home/airflow/spark-venv/bin/pip install --no-cache-dir pyspark==3.5.8
