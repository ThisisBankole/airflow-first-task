from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.dates import days_ago
import time
from random import choice
from airflow.models import Variable

default_args = {
    'owner': 'workflow',
}

def has_driving_license():
    return choice([True, False])

def branch(ti):
    if ti.xcom_pull(task_ids='has_driving_license'):
        return 'eligible_to_drive'
    else:
        return 'not_eligible_to_drive'
    
    
def eligible_to_drive():
    print('Eligible to drive')
    
def not_eligible_to_drive():
    print('Not eligible to drive')
    
    
with DAG(
    dag_id='branching',
    default_args=default_args,
    description='branching',
    start_date= days_ago(1),
    schedule_interval='@once',
    tags=['python','branching']
) as dag:
    
    has_driving_license = PythonOperator(
        task_id='has_driving_license',
        python_callable=has_driving_license,
    )
    
    branch = BranchPythonOperator(
        task_id='branch',
        python_callable=branch,
    )
    
    eligible_to_drive = PythonOperator(
        task_id='eligible_to_drive',
        python_callable=eligible_to_drive,
    )
    
    not_eligible_to_drive = PythonOperator(
        task_id='not_eligible_to_drive',
        python_callable=not_eligible_to_drive,
    )
    
has_driving_license >> branch >> [eligible_to_drive, not_eligible_to_drive]