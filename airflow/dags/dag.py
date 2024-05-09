from airflow import DAG
from tasks.build_graph import build_graph
from tasks.web_srape import web_scrape
from tasks.clean_data import clean_data
from tasks.find_keyword import find_keyword
from tasks.transform_data import transform_data
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 5, 5),
    'retries': 0,
}


dag = DAG(
    'DSDE',
    default_args=default_args,
    description='From_scrape_to_graph_info',
    schedule='@daily',
    catchup=False
)

scrape_task = PythonOperator(
    task_id='Scrape_web_from_arxiv',
    python_callable=web_scrape,
    dag=dag,
)

clean_task = PythonOperator(
    task_id='Clean_abstract',
    python_callable=clean_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='Transform_abstract_to_Vector_and_find_similarity_vector',
    python_callable=transform_data,
    dag=dag,
)

build_task = PythonOperator(
    task_id='Build_graph_node_information_and_cluster',
    python_callable=build_graph,
    dag=dag,
)

keyword_task = PythonOperator(
    task_id='Find_keyword_in_each_network_cluster',
    python_callable=find_keyword,
    dag=dag,
)

scrape_task >> clean_task >> transform_task >> build_task >> keyword_task