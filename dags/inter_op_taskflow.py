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
import pandas as pd

default_args = {
    'owner': 'workflow',
}

@dag(
    dag_id='inter_op_taskflow',
    description='interops tasks using TaskFlow API',
    default_args=default_args,
    schedule_interval='@once',
    start_date=days_ago(1),
    tags=['branching_op, python']
    )
def inter_op_taskflow():
    
    
    
    def read_csv():
        df = pd.read_csv('/Users/b/airflow/datasets/car_data.csv')
        
        print(df)
        
        return df.to_json() 
    
    @task
    def filter_tesla(json_data):
        df = pd.read_json(json_data)
        
        tesla_df = df[df['Brand'] == 'Tesla']
        
        return tesla_df.to_json()
    
    
    def write_csv_result(filtered_teslas_json):
        
        df = pd.read_json(filtered_teslas_json)
        
        df.to_csv('/Users/b/airflow/output/teslas.csv', index=False)
        
        
    
    read_csv_task = PythonOperator(
        task_id='read_csv_task',
        python_callable=read_csv
        )
    
    
    filtered_teslas_json = filter_tesla(read_csv_task.output)
    
    
    write_csv_result_task = PythonOperator(
        task_id='write_csv_result_task',
        python_callable=write_csv_result,
        op_kwargs={'filtered_teslas_json': filtered_teslas_json}
        )


inter_op_taskflow()

