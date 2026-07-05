from airflow.decorators import dag, task
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/home/mohamed/energy-flow-intelligence')

from extract.rte_client import get_token, get_production_data

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

@dag(
    dag_id='energy_pipeline',
    default_args=default_args,
    schedule='*/5 * * * *',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['energy', 'rte']
)
def energy_pipeline():

    @task()
    def extract():
        token = get_token()
        data = get_production_data(token)
        return data

    @task()
    def load(data):
        print(f"Data received: {len(data['actual_generations_per_production_type'])} production types")
        # BigQuery loading will be added here
        return "success"

    data = extract()
    load(data)

energy_pipeline()