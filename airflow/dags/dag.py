from airflow import DAG
from tasks.build_graph import build_graph
from tasks.clean_data import clean_data
from tasks.find_keyword import find_keyword
from tasks.transform_data import transform_data
from tasks.transform_data import web_scrape
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}


dag = DAG(
    'DSDE',
    default_args=default_args,
    description='From scrape to graph info',
    schedule_interval=timedelta(days=1),
)

scrape_task = PythonOperator(
    task_id='Scrape web from arxiv',
    python_callable=web_scrape,
    dag=dag,
)

clean_task = PythonOperator(
    task_id='Clean abstract',
    python_callable=clean_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='Transform abstract to Vector and find similarity vector',
    python_callable=transform_data,
    dag=dag,
)

build_task = PythonOperator(
    task_id='Build graph node information and cluster',
    python_callable=build_graph,
    dag=dag,
)

keyword_task = PythonOperator(
    task_id='Find keyword in each network cluster',
    python_callable=find_keyword,
    dag=dag,
)

clean_task >> transform_data >> build_graph >> find_keyword
