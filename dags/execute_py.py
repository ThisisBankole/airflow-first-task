from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import time

default_args = {
    'owner': 'workflow',
}


#def task_a():
 #   print('task A executed')
        
#def task_b():
 #   time.sleep(5)
  #  print('task B executed')

#def task_c():
    
 #   print('task C executed')

#def task_d():
   
 #   print('task D executed')

def greet_person(name):
    print(f'Hello {name}')
    
def greet_city(name, city):
    print(f'Hello, {name} from {city}')
    
with DAG(
    dag_id='execute_python',
    default_args=default_args,
    description='A simple py operator DAG',
    start_date= days_ago(1),
    schedule_interval='@daily',
    tags=['python','simple']
) as dag:
    taskA = PythonOperator(
        task_id='greet_person',
        python_callable=greet_person,
        op_kwargs={'name': 'Bob'}
    )
    
    taskB = PythonOperator(
        task_id='greet_city',
        python_callable=greet_city,
        op_kwargs={'name': 'Bob', 'city': 'New York'}
    )
    
    
taskA >> taskB