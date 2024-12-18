from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from google.cloud import storage
from google.cloud import spanner
import pandas as pd
import io

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': 300,
}

dag = DAG(
    'itjobs_data_to_spanner',
    default_args=default_args,
    schedule_interval=None
)

def get_itjobs_files():
    storage_client = storage.Client()
    bucket = storage_client.bucket('itjobs_1212')
    blobs = bucket.list_blobs(prefix='itjobs')
    return [blob.name for blob in blobs]

def load_to_dataframe(ti):
    storage_client = storage.Client()
    bucket = storage_client.bucket('itjobs_1212')
    file_names = ti.xcom_pull(task_ids='get_itjobs_files')

    dfs = []
    for file_name in file_names:
        blob = bucket.blob(file_name)
        data = blob.download_as_bytes()
        df = pd.read_csv(io.BytesIO(data), header=0)
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df['Year'] = pd.to_datetime(combined_df['Year'])
    combined_df['Impacting_Event'] = combined_df['Impacting_Event'].astype("str")
    combined_df['Job_Loss_Percentage_Due_to_Event'] = combined_df['Job_Loss_Percentage_Due_to_Event'].astype("str")
    combined_df['New_Emerging_IT_Roles'] = combined_df['New_Emerging_IT_Roles'].astype("str")
    ext_year = combined_df['Year'].dt.year
    combined_df['Total_IT_Job_Openings_Mean'] = combined_df.groupby(ext_year)['Total_IT_Job_Openings'].transform(lambda x: x.mean())
    combined_df = combined_df.dropna(subset=['Total_IT_Job_Openings'])
    ti.xcom_push(key='dataframe', value=combined_df.to_csv(index=False))

def load_to_spanner(ti):
    spanner_client = spanner.Client()
    instance = spanner_client.instance('itspanner')
    database = instance.database('itdatabase12')

    df = pd.read_csv(io.StringIO(ti.xcom_pull(key='dataframe', task_ids='load_to_dataframe')))

    with database.batch() as batch:
        batch.insert(
            table='ittable12',
            columns=df.columns.tolist(),
            values=[tuple(row) for row in df.values]
        )

get_itjobs_files = PythonOperator(
    task_id='get_itjobs_files',
    python_callable=get_itjobs_files,
    dag=dag
)

load_to_dataframe = PythonOperator(
    task_id='load_to_dataframe',
    python_callable=load_to_dataframe,
    op_args=[],
    dag=dag
)

load_to_spanner = PythonOperator(
    task_id='load_to_spanner',
    python_callable=load_to_spanner,
    op_args=[],
    dag=dag
)

get_itjobs_files >> load_to_dataframe >> load_to_spanner