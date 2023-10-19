from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import time

default_args = {
    'owner': 'workflow',
}


def increment_by_one(value):
    print(f'Value is {value}')
    return value + 1


def multiply_by_100(ti):
    value = ti.xcom_pull(task_ids='increment_by_one')
   
    print(f'value is {value}')
    return value * 100


def subtract_by_9(ti):
    value = ti.xcom_pull(task_ids='multiply_by_100')
    print(f'value is {value}')
    return value - 9

def print_value(ti):
    value = ti.xcom_pull(task_ids='subtract_by_9')
    print(f'value is {value}')
    #return value - 9

with DAG(
    dag_id='CRossComm',
    default_args=default_args,
    description='cross communication between tasks',
    start_date= days_ago(1),
    schedule_interval='@daily',
    tags=['python','xcom']
) as dag:
    increment_by_one = PythonOperator(
        task_id='increment_by_one',
        python_callable=increment_by_one,
        op_kwargs={'value': 1},
        provide_context=True
    )
    
    multiply_by_100 = PythonOperator(
        task_id='multiply_by_100',
        python_callable=multiply_by_100,
    )
    subtract_by_9 = PythonOperator(
        task_id='subtract_by_9',
        python_callable=subtract_by_9,
    )
    print_value = PythonOperator(
        task_id='print_value',
        python_callable=print_value,
    )

increment_by_one >> multiply_by_100 >> subtract_by_9 >> print_value