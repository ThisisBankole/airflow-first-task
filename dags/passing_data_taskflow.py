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

@dag(
    dag_id='passing_data_dags_taskflow',
    description='DAG using TaskFlow API',
    default_args=default_args, 
    schedule_interval='@once',
    start_date=days_ago(1), 
    tags=['taskflow']
    )
def passing_data_with_taskflow_api():
    
    @task
    def get_order_prices():
        
        order_price_data = {
            'o1': 100,
            'o2': 200,
            'o3': 300,
            'o4': 400,
            'o5': 500,
            'o6': 600,
        }
        
        return order_price_data
    
   
    @task(multiple_outputs=True)
    def compute_sum_and_average(order_price_data: dict):
        
        total = 0
        count = 0
        for order in order_price_data:
            total += order_price_data[order]
            count += 1
            
        average = total / count
        
        return {'total': total, 'average': average}
    
    
    @task
    def display_results(total, average):
        
        print(f'Total: {total}')
        print(f'Average: {average}')
        
    
        
        
    order_price_data = get_order_prices()
    
    price_summary_data = compute_sum_and_average(order_price_data)
    
    display_results(
        price_summary_data['total'],
        price_summary_data['average']
        )
    
    
passing_data_with_taskflow_api()
    
    