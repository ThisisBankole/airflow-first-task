from datetime import datetime, timedelta
from airflow import DAG

from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.dates import days_ago
import time
from random import choice

from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    'owner': 'workflow',
}

def choose_branch():
    return choice([True, False])

def branch(ti):
    if ti.xcom_pull(task_ids='taskChooseBranch'):
        return 'TaskC'
    else:
        return 'TaskD'
    
    
def task_c():
    print('task C executed')
    

with DAG(
    dag_id='cron_backfills',
    default_args=default_args,
    description='A simple cron backfill DAG',
    start_date= days_ago(30),
    schedule_interval='0 */12 * * 6,0',
    catchup=False,
    tags=['cron','simple', 'backfill']
) as dag:
    
    taskA = BashOperator(
        task_id='taskA',
        bash_command='echo "task A executed"'
    )
    
    taskChooseBranch = PythonOperator(
        task_id='taskChooseBranch',
        python_callable=choose_branch,
    )
    
    taskBranch = BranchPythonOperator(
        task_id='taskBranch',
        python_callable=branch,
    )
    
    taskC = PythonOperator(
        task_id='TaskC',
        python_callable=task_c,
    )
    
    taskD = BashOperator(
        task_id='TaskD',
        bash_command='echo "task D executed"'
    )
    
    taskE = EmptyOperator(
        task_id='TaskE'
    )
    
    
taskA >> taskChooseBranch >> taskBranch >> [taskC, taskE]

taskC >> taskD