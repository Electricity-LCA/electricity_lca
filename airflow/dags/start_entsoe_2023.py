import textwrap
from datetime import datetime, timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
with DAG(
    "entsoe_2023",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="A simple tutorial DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2024, 5, 17),
    catchup=False,
    tags=["example"],
) as dag:

    t1 = BashOperator(
        task_id="extract_from_entsoe",
        bash_command="python /home/artur/PycharmProjects/electricity_lca/src/pipelines/retrieve_from_entsoe.py -s 20230101 -e 20230301",
    )
