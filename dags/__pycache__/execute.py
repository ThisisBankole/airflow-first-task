from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'workflow'
}


with DAG(
    dag_id='execute',
    default_args=default_args,
    description='execute mutlilple tasks',
    start_date=days_ago(1),
    schedule_interval= timedelta(days=1),
    tags=['upstream', 'downstream'],
    template_searchpath= '/Users/b/airflow/dags/bash'
    
) as dag:
    
    taskA = BashOperator(
        task_id='taskA',
        bash_command= 'taskA.sh'
    )
    
    taskB = BashOperator(
        task_id='taskB',
        bash_command= 'taskB.sh'
    )
    
    taskC = BashOperator(
        task_id='taskC',
        bash_command= 'taskC.sh'
    )
    
    taskD = BashOperator( 
        task_id='taskD',
        bash_command= 'taskD.sh'
    )
    taskE = BashOperator(
        task_id='taskE',
        bash_command= 'taskE.sh'
    )
    taskF = BashOperator(
        task_id='taskF',
        bash_command= 'taskF.sh'
    )
    taskG = BashOperator(
        task_id='taskG',
        bash_command= 'taskG.sh'
    )

taskA >> taskB >> taskE
taskA >> taskC >> taskF
taskA >> taskD >> taskG
