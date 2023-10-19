import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import time

default_args = {
    'owner': 'workflow',
}

def read_csv():
    df = pd.read_csv('/Users/b/airflow/datasets/insurance.csv')
    print(df)
    return df.to_json()

def remove_nulls(**kwargs):
    ti = kwargs['ti']
    
    json_data = ti.xcom_pull(task_ids='read_csv')
    
    df = pd.read_json(json_data)
    
    df = df.dropna()
    
    print(df)
    
    return df.to_json()


def groupby_smokers(ti):
    json_data = ti.xcom_pull(task_ids='remove_nulls')
    
    df = pd.read_json(json_data)
    
    smoker_df = df.groupby('smoker').agg({
        'age': 'mean',
        'bmi': 'mean',
        'charges': 'mean'
    }).reset_index()
    
    smoker_df.to_csv('/Users/b/airflow/output/smoker.csv', index=False)
    


def groupby_region(ti):
    json_data = ti.xcom_pull(task_ids='remove_nulls')
    
    df = pd.read_json(json_data)
    
    region_df = df.groupby('region').agg({
        'age': 'mean',
        'bmi': 'mean',
        'charges': 'mean'
    }).reset_index()
    
    region_df.to_csv('/Users/b/airflow/output/region.csv', index=False)


with DAG(
    dag_id='pipeline',
    description='pipeline running',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval= '@once',
    tags=['pipeline', 'python']
) as dag:
    read_csv = PythonOperator(
        task_id='read_csv',
        python_callable=read_csv
    )
    
    remove_nulls = PythonOperator(
        task_id='remove_nulls',
        python_callable=remove_nulls,
        provide_context=True
    )
    groupby_smokers = PythonOperator(
        task_id='groupby_smokers',
        python_callable=groupby_smokers,
        provide_context=True
    )
    groupby_region = PythonOperator(
        task_id='groupby_region',
        python_callable=groupby_region,
        provide_context=True
    )
    
read_csv >> remove_nulls >> [groupby_smokers, groupby_region]