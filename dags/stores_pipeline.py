import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import time
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
from airflow.utils.edgemodifier import Label



default_args = {
    'owner': 'workflow',
}



STORES_DATASETS= '/Users/b/airflow/datasets/ColesStoreData.csv'



SALES_DATASETS= '/Users/b/airflow/datasets/ColesSalesData.csv'




def read_csv_sales(ti):
    df = pd.read_csv(SALES_DATASETS)
    
    print(df)
    
    ti.xcom_push(key='sales_csv', value=df.to_json())




def read_csv_stores(ti):
    df = pd.read_csv(STORES_DATASETS)
    
    print(df)
    
    ti.xcom_push(key='stores_csv', value=df.to_json())




def remove_nulls_sales(ti):
    json_data = ti.xcom_pull(key='sales_csv')
    
    df = pd.read_json(json_data)
    
    df = df.dropna()
    
    print(df)
    
    ti.xcom_push(key='sales_clean_csv', value=df.to_json())
    

    
def remove_nulls_stores(ti):
    json_data = ti.xcom_pull(key='stores_csv')
    
    df = pd.read_json(json_data)
    
    df = df.dropna()
    
    print(df)
    
    ti.xcom_push(key='stores_clean_csv', value=df.to_json())
 


def join_sales_stores(ti):
    sales_data = ti.xcom_pull(key='sales_clean_csv')
    stores_data = ti.xcom_pull(key='stores_clean_csv')
    
    df_stores = pd.read_json(stores_data)
    df_sales = pd.read_json(sales_data)
    
    join_data = pd.merge (
        df_sales, 
        df_stores, 
        left_on='Coles_StoreIDNo',
        right_on= 'Coles_StoreID',
        how='inner'
    )
    join_data.to_csv('/Users/b/airflow/output/join.csv', index=False)
    
    print(join_data)
    
    ti.xcom_push(key='join_csv', value=join_data.to_json())
     

    
def determine_branch():
    data_action = Variable.get('data_action', default_var=None)
    print(data_action)
    
    if data_action.startswith('filter'):
        return "filtering.{0}".format(data_action)
    elif data_action == 'groupby_location':
        return "grouping.{0}".format(data_action)
    


def filter_by_vic(ti):
    json_data = ti.xcom_pull(key='join_csv')
    df = pd.read_json(json_data)
    region_df = df[df['Store_Location'] == 'VIC']
    region_df.to_csv('/Users/b/airflow/output/victoria.csv', index=False)
  
  
  
def filter_by_nsw(ti):
    json_data = ti.xcom_pull(key='join_csv')
    df = pd.read_json(json_data)
    region_df = df[df['Store_Location'] == 'NSW']
    region_df.to_csv('/Users/b/airflow/output/nsw.csv', index=False)


def filter_by_qld(ti):
    json_data = ti.xcom_pull(key='join_csv')
    df = pd.read_json(json_data)
    region_df = df[df['Store_Location'] == 'QLD']
    region_df.to_csv('/Users/b/airflow/output/qld.csv', index=False)

    
def filter_by_wa(ti):
    json_data = ti.xcom_pull(key='join_csv')
    df = pd.read_json(json_data)
    region_df = df[df['Store_Location'] == 'WA']
    region_df.to_csv('/Users/b/airflow/output/wa.csv', index=False)
    
    
def filter_by_sa(ti):
    json_data = ti.xcom_pull(key='join_csv')
    df = pd.read_json(json_data)
    region_df = df[df['Store_Location'] == 'SA']
    region_df.to_csv('/Users/b/airflow/output/sa.csv', index=False)
    
def filter_by_nt(ti):
    json_data = ti.xcom_pull(key='join_csv')
    df = pd.read_json(json_data)
    region_df = df[df['Store_Location'] == 'NT']
    region_df.to_csv('/Users/b/airflow/output/nt.csv', index=False)
    
    
def filter_by_act(ti):
    json_data = ti.xcom_pull(key='join_csv')
    df = pd.read_json(json_data)
    region_df = df[df['Store_Location'] == 'ACT']
    region_df.to_csv('/Users/b/airflow/output/act.csv', index=False)
    
def filter_by_tas(ti):
    json_data = ti.xcom_pull(key='join_csv')
    df = pd.read_json(json_data)
    region_df = df[df['Store_Location'] == 'TAS']
    region_df.to_csv('/Users/b/airflow/output/tas.csv', index=False)
    

def groupby_location(ti):
    json_data = ti.xcom_pull(key='join_csv')
    
    df = pd.read_json(json_data)
    
    region_df = df.groupby('Store_Location').agg({
        'Customer_Count': 'sum',
        'Staff_Count': 'sum',
        'Store_Area': 'sum',
        'Coles_StoreID': lambda x: x.nunique(),
        'Expec_Revenue': 'sum',
        'Gross_Sale': 'sum',
        'Sales_Cost': 'sum'
    }).reset_index()
    
    region_df.to_csv('/Users/b/airflow/output/grouped_by_location.csv', index=False)
    
    region_df = df.groupby('Coles_Forecast').agg({
        'Customer_Count': 'sum',
        'Staff_Count': 'sum',
        'Store_Area': 'sum',
        'Coles_StoreID': lambda x: x.nunique(),
        'Expec_Revenue': 'sum',
        'Gross_Sale': 'sum',
        'Sales_Cost': 'sum'
    }).reset_index()
    
    region_df.to_csv('/Users/b/airflow/output/grouped_by_forecast.csv', index=False)
    
    
    
with DAG(
        dag_id='stores_pipeline',
        description='stores_pipeline',
        default_args=default_args,
        start_date=days_ago(1),
        schedule_interval= '@once',
        tags=['stores', 'python']
    ) as dag:
        
        with TaskGroup('reading_and_preprocessing') as reading_and_preprocessing:
            
            read_csv_sales = PythonOperator(
                task_id='read_csv_sales',
                python_callable=read_csv_sales
            )
            
            read_csv_stores = PythonOperator(
                task_id='read_csv_stores',
                python_callable=read_csv_stores
            )
            
            remove_nulls_sales = PythonOperator(
                task_id='remove_nulls_sales',
                python_callable=remove_nulls_sales
            )
            
            remove_nulls_stores = PythonOperator(
                task_id='remove_nulls_stores',
                python_callable=remove_nulls_stores
            )
            
            join_sales_stores = PythonOperator(
                task_id='join_sales_stores',
                python_callable=join_sales_stores
            )
            
            read_csv_sales >> read_csv_stores >> remove_nulls_sales >> remove_nulls_stores >> join_sales_stores
            
        determine_branch = PythonOperator(
            task_id='determine_branch',
            python_callable=determine_branch,
        )
        
        with TaskGroup('filtering') as filtering:
            
            filter_by_vic = PythonOperator(
                task_id='filter_by_vic',
                python_callable=filter_by_vic,
            )
            
            filter_by_nsw = PythonOperator(
                task_id='filter_by_nsw',
                python_callable=filter_by_nsw,
            )   
            
            filter_by_qld = PythonOperator(
                task_id='filter_by_qld',
                python_callable=filter_by_qld,
            )
            
            filter_by_wa = PythonOperator(
                task_id='filter_by_wa',
                python_callable=filter_by_wa,
            )
            
            filter_by_sa = PythonOperator(
                task_id='filter_by_sa',
                python_callable=filter_by_sa,
            )
            
            filter_by_nt = PythonOperator(
                task_id='filter_by_nt',
                python_callable=filter_by_nt,
            )
            
            filter_by_act = PythonOperator(
                task_id='filter_by_act',
                python_callable=filter_by_act,
            )
            
            filter_by_tas = PythonOperator(
                task_id='filter_by_tas',
                python_callable=filter_by_tas,
            )
            
            
            
            
        with TaskGroup('grouping') as grouping:
                
                groupby_location = PythonOperator(
                    task_id='groupby_location',
                    python_callable=groupby_location,
                )
                
                
        
        reading_and_preprocessing >> Label('preprocessed data') >> determine_branch >> Label('branch on condition') >> [filtering, grouping]
    
        