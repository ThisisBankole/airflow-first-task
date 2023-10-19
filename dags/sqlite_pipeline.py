import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.utils.dates import days_ago
import time

default_args = {
    'owner': 'workflow',
}

with DAG(
    dag_id='execute_sqlite_pipeline',
    default_args=default_args,
    description='Pipeline to execute sqlite operations',
    start_date= days_ago(1),
    schedule_interval='@once',
    tags=['pipeline','sqlite']
) as dag:
    create_table = SqliteOperator(
        task_id='create_table',
        sql = r"""
            CREATE TABLE IF NOT EXISTS new_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    city TEXT,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
        """,
        sqlite_conn_id='db_sqlite_conn',
        dag=dag,
    )
    
    insert_data = SqliteOperator(
        task_id='insert_data',
        sql = r"""
            INSERT INTO new_users (name, age, is_active) VALUES
            ('Bob', 23, true),
            ('Alice', 25, true),
            ('John', 27, false),
            ('Jane', 21, true);
        """,
        sqlite_conn_id='db_sqlite_conn',
        dag=dag,
    )
    
    insert_data2 = SqliteOperator(
        task_id='insert_data2',
        sql = r"""
            INSERT INTO new_users (name, age) VALUES
                ('Seun', 23),
                ('Ali', 25),
                ('Tunde', 27),
                ('Muna', 21);
        """,
        sqlite_conn_id='db_sqlite_conn',
        dag=dag,
    )
    
    delete_data = SqliteOperator(
        task_id='delete_data',
        sql = r"""
            DELETE FROM new_users WHERE is_active = 0;
        """,
        sqlite_conn_id='db_sqlite_conn',
        dag=dag,
    )
    
    update_data = SqliteOperator(
        task_id='update_data',
        sql = r"""
            UPDATE new_users SET city = 'Manchester';
        """,
        sqlite_conn_id='db_sqlite_conn',
        dag=dag,
    )
    
        
    display_data = SqliteOperator(
        task_id='display_data',
        sql = r"""
            SELECT * FROM new_users;
        """,
        sqlite_conn_id='db_sqlite_conn',
        dag=dag,
        do_xcom_push=True
    )
        
    
create_table >> [insert_data, insert_data2] >> delete_data >> update_data >> display_data