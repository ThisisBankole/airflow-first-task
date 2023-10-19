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
    dag_id='branching_op_taskflow',
    description='DAG using BranchingOperator and TaskFlow API',
    default_args=default_args,
    schedule_interval='@once',
    start_date=days_ago(1),
    tags=['branching_op']
    )

def branching_op_with_taskflow_api():  
    
    @task(task_id='read_csv_file_task')
    def read_csv():
        df = pd.read_csv('/Users/b/airflow/datasets/car_data.csv')
        
        print(df)
        
        return df.to_json()
    
    
    @task.branch
    def determine_branch():
        final_output = Variable.get('transform', default_var=None)
        
        if final_output == 'filter_two_seaters':
            return 'filter_two_seaters_task'
        elif final_output == 'filter_fwds':
            return 'filter_fwds_task'
        

    @task(task_id='filter_two_seaters_task')
    def filter_two_seaters(**kwargs):
        ti = kwargs['ti']
    
        json_data = ti.xcom_pull(task_ids='read_csv_file_task')
        
        df = pd.read_json(json_data)
        
        two_seaters_df = df[df['Seats'] == 2]
        
        ti.xcom_push(key='transform_result', value=two_seaters_df.to_json())
        
        ti.xcom_push(key='transform_filename', value='two_seaters')
        

    @task(task_id='filter_fwds_task')
    def filter_fwds(**kwargs):
        ti = kwargs['ti']
        json_data = ti.xcom_pull(task_ids='read_csv_file_task')
        
        df = pd.read_json(json_data)
        
        fwds_df = df[df['PowerTrain'] == 'FWD']
        
        ti.xcom_push(key='transform_result', value=fwds_df.to_json())
        
        ti.xcom_push(key='transform_filename', value='fwds') 
     
     
        
    @task(trigger_rule='none_failed', task_id='write_csv_task')
    def write_csv(**kwargs):
        ti = kwargs['ti']
        json_data = ti.xcom_pull(key='transform_result')
        
        filename = ti.xcom_pull(key='transform_filename')
        
        df = pd.read_json(json_data)
        
        df.to_csv(f'/Users/b/airflow/output/{filename}.csv', index=False)
        
    
    
    read_csv() >> determine_branch() >> [filter_two_seaters(), filter_fwds()] >> write_csv()
    
    
branching_op_with_taskflow_api()
    