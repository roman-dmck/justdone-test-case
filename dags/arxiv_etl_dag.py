from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl.main import etl_pipeline

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 5, 21),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "arxiv_etl_dag",
    default_args=default_args,
    description="ETL pipeline for processing papers from arXiv",
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:
    extract_task = PythonOperator(
        task_id="extract_papers",
        python_callable=etl_pipeline(),
    )

    extract_task
