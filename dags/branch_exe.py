from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.dates import days_ago
import time
from random import choice
from airflow.models import Variable
import pandas as pd
from airflow.utils.task_group import TaskGroup
from airflow.utils.edgemodifier import Label


default_args = {
    'owner': 'workflow',
}

DATASETS_PATH = '/Users/b/airflow/datasets/insurance.csv'

OUTPUT_PATH = '/Users/b/airflow/output/{0}.csv'


def read_csv(ti):
    df = pd.read_csv(DATASETS_PATH)
    
    print(df)
    
    #return df.to_json()
    ti.xcom_push(key='my_csv', value=df.to_json())


def remove_nulls(ti):
    
    json_data = ti.xcom_pull(key='my_csv')
    
    df = pd.read_json(json_data)
    
    df = df.dropna()
    
    print(df)
    
    #return df.to_json()
    ti.xcom_push(key='my_clean_csv', value=df.to_json())


def determine_branch():
    transform_action = Variable.get('transform_action', default_var=None)
    print(transform_action)
    
    if transform_action.startswith('filter'):
        return "filtering.{0}".format(transform_action)
    elif transform_action == 'groupby_smokers':
        return "grouping.{0}".format(transform_action)
    
    
def filter_by_southwest(ti):
    json_data = ti.xcom_pull(key='my_clean_csv')
    df = pd.read_json(json_data)
    region_df = df[df['region'] == 'southwest']
    region_df.to_csv(OUTPUT_PATH.format('southwest'), index=False)
    
def filter_by_southeast(ti):
    json_data = ti.xcom_pull(key='my_clean_csv')
    df = pd.read_json(json_data)
    region_df = df[df['region'] == 'southeast']
    region_df.to_csv(OUTPUT_PATH.format('southeast'), index=False)
    
    
def filter_by_northwest(ti):
    json_data = ti.xcom_pull(key='my_clean_csv')
    df = pd.read_json(json_data)
    region_df = df[df['region'] == 'northwest']
    region_df.to_csv(OUTPUT_PATH.format('northwest'), index=False)
    
    
def filter_by_northeast(ti):
    json_data = ti.xcom_pull(key='my_clean_csv')
    df = pd.read_json(json_data)
    region_df = df[df['region'] == 'northeast']
    region_df.to_csv(OUTPUT_PATH.format('northeast'), index=False)
    
    

def groupby_smokers(ti):
    json_data = ti.xcom_pull(key='my_clean_csv')
    
    df = pd.read_json(json_data)
    
    smoker_df = df.groupby('region').agg({
        'age': 'mean',
        'bmi': 'mean',
        'charges': 'mean'
    }).reset_index()
    
    smoker_df.to_csv(OUTPUT_PATH.format('grouped_by_region'), index=False)
    
    smoker_df = df.groupby('smoker').agg({
        'age': 'mean',
        'bmi': 'mean',
        'charges': 'mean'
    }).reset_index()
    
    smoker_df.to_csv(OUTPUT_PATH.format('grouped_by_smoker'), index=False)
    
    
    
with DAG(
    dag_id='branch_exe',
    default_args=default_args,
    description='branch_exe',
    start_date= days_ago(1),
    schedule_interval='@once',
    tags=['python','branching', 'transform', 'filter', 'groupby']
) as dag:
    
    with TaskGroup('reading_and_preprocessing') as reading_and_preprocessing:
    
        read_csv = PythonOperator(
            task_id='read_csv',
            python_callable=read_csv,
        )
        
        remove_nulls = PythonOperator(
            task_id='remove_nulls',
            python_callable=remove_nulls,
        )
        
        read_csv >> remove_nulls
        
    determine_branch = BranchPythonOperator(
        task_id='determine_branch',
        python_callable=determine_branch,
    )
    
    with TaskGroup('filtering') as filtering:
        
        filter_by_southwest = PythonOperator(
            task_id='filter_by_southwest',
            python_callable=filter_by_southwest,
        )
        
        filter_by_southeast = PythonOperator(
            task_id='filter_by_southeast',
            python_callable=filter_by_southeast,
        )
        
        filter_by_northwest = PythonOperator(
            task_id='filter_by_northwest',
            python_callable=filter_by_northwest,
        )
        
        filter_by_northeast = PythonOperator(
            task_id='filter_by_northeast',
            python_callable=filter_by_northeast,
        )
    
    with TaskGroup('grouping') as grouping:
        
        groupby_smokers = PythonOperator(
            task_id='groupby_smokers',
            python_callable=groupby_smokers,
        )
        
    
    reading_and_preprocessing >> Label('preprocessed_data') >> determine_branch >> Label('branch on condition') >> [filtering, grouping]