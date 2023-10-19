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

def read_csv():
    df = pd.read_csv('/Users/b/airflow/datasets/car_data.csv')
    
    print(df)
    
    return df.to_json()

def determine_branch():
    final_output = Variable.get('transform', default_var=None)
    
    if final_output == 'filter_two_seaters':
        return 'filter_two_seaters_task'
    elif final_output == 'filter_fwds':
        return 'filter_fwds_task'
    

def filter_two_seaters(ti):
    json_data = ti.xcom_pull(task_ids='read_csv_file_task')
    
    df = pd.read_json(json_data)
    
    two_seaters_df = df[df['Seats'] == 2]
    
    ti.xcom_push(key='transform_result', value=two_seaters_df.to_json())
    
    ti.xcom_push(key='transform_filename', value='two_seaters')
    

def filter_fwds(ti):
    json_data = ti.xcom_pull(task_ids='read_csv_file_task')
    
    df = pd.read_json(json_data)
    
    fwds_df = df[df['PowerTrain'] == 'FWD']
    
    ti.xcom_push(key='transform_result', value=fwds_df.to_json())
    
    ti.xcom_push(key='transform_filename', value='fwds') 
    

def write_csv(ti):
    json_data = ti.xcom_pull(key='transform_result')
    
    filename = ti.xcom_pull(key='transform_filename')
    
    df = pd.read_json(json_data)
    
    df.to_csv(f'/Users/b/airflow/output/{filename}.csv', index=False)
  

with DAG(
    dag_id='branching_op',
    description='DAG using BranchingOperator',
    default_args=default_args,
    schedule_interval='@once',
    start_date=days_ago(1),
    tags=['branching_op']
    ) as dag:
    
    read_csv_file_task = PythonOperator(
        task_id='read_csv_file_task',
        python_callable=read_csv
        )
    
    branch_task = PythonOperator(
        task_id='branch_task',
        python_callable=determine_branch
        )
    
    filter_two_seaters_task = PythonOperator(
        task_id='filter_two_seaters_task',
        python_callable=filter_two_seaters
        )
    
    filter_fwds_task = PythonOperator(
        task_id='filter_fwds_task',
        python_callable=filter_fwds
        )
    
    write_csv_task = PythonOperator( # PythonOperator(task_id='write_csv_task', python_callable=write_csv trigger_rule='none_failed')
        task_id='write_csv_task',
        python_callable=write_csv,
        trigger_rule='none_failed'
        )
        
    
    read_csv_file_task >> branch_task >> \
    [filter_two_seaters_task, filter_fwds_task] >> write_csv_task
    
        
    