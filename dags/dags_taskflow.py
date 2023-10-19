from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import time
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
from airflow.utils.edgemodifier import Label
from airflow.decorators import task, dag


default_args = {
    'owner': 'workflow',
}

@dag(
    dag_id='dags_taskflow',
    description='DAG using TaskFlow API',
    default_args=default_args, 
    schedule_interval='@once',
    start_date=days_ago(1), 
    tags=['taskflow']
    )
def dag_with_taskflow_api():
    
    @task
    def task_a():
        print('task_a')
        time.sleep(5)
        print('task_a done')
        
    @task
    def task_b():
        print('task_b')
        time.sleep(5)
        print('task_b done')
        
    @task
    def task_c():
        print('task_c')
        time.sleep(5)
        print('task_c done')
        
        
    @task
    def task_d():
        print('task_d')
        time.sleep(5)
        print('task_d done')
        
    task_a() >> [task_b(), task_c()] >> task_d()



dag_with_taskflow_api()
        
 