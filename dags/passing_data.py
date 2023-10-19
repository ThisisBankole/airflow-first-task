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

import json



default_args = {
    'owner': 'workflow',
}


def get_order_prices(**kwargs):
    ti = kwargs['ti']
    
    order_price_data = {
        'o1': 100,
        'o2': 200,
        'o3': 300,
        'o4': 400,
        'o5': 500,
        'o6': 600,
    }
    
    order_price_data_json = json.dumps(order_price_data)
    
    ti.xcom_push(key='order_price_data', value=order_price_data_json)
    

def compute_sum(**kwargs):
    ti = kwargs['ti']
    
    order_price_data_json = ti.xcom_pull(key='order_price_data', task_ids='get_order_prices')
    
    print(order_price_data_json)
    
    order_price_data = json.loads(order_price_data_json)
    
    total = 0
    for order in order_price_data:
        total += order_price_data[order]
    
    #order_sum = sum(order_price_data.values())
    
    print(total)
    
    ti.xcom_push(key='total_price', value=total)
    

def compute_average(**kwargs):
    ti = kwargs['ti']
    
    order_price_data_json = ti.xcom_pull(key='order_price_data', task_ids='get_order_prices')
    
    print(order_price_data_json)
    
    order_price_data = json.loads(order_price_data_json)
    
    total = 0
    count = 0
    
    for order in order_price_data:
        total += order_price_data[order]
        count += 1
    
    average = total / count
    
    print(average)
    
    ti.xcom_push(key='average_price', value=average)
    

def display_results(**kwargs):
    ti = kwargs['ti']
    
    total_price = ti.xcom_pull(key='total_price', task_ids='compute_sum')
    
    average_price = ti.xcom_pull(key='average_price', task_ids='compute_average')
    
    print(f'Total price: {total_price}')
    print(f'Average price: {average_price}')
    
    
with DAG(
    dag_id='passing_data',
    description='DAG passing data between tasks',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval= '@once',
    tags=['passing_data', 'python']
) as dag:
    get_order_prices = PythonOperator(
        task_id='get_order_prices',
        python_callable=get_order_prices
    )
    
    compute_sum = PythonOperator(
        task_id='compute_sum',
        python_callable=compute_sum
    )
    
    compute_average = PythonOperator(
        task_id='compute_average',
        python_callable=compute_average
    )
    
    display_results = PythonOperator(
        task_id='display_results',
        python_callable=display_results
    )
    
    get_order_prices >> [compute_sum, compute_average] >> display_results