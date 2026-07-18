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
        from google.cloud import bigquery
        
        client = bigquery.Client(project="project-da2d9305-97cf-4aec-9f3")
        table_id = "project-da2d9305-97cf-4aec-9f3.energy_data.production_by_type"
        
        rows = []
        for item in data["actual_generations_per_production_type"]:
            production_type = item["production_type"]
            for value in item["values"]:
                rows.append({
                    "production_type": production_type,
                    "start_date": value["start_date"],
                    "end_date": value["end_date"],
                    "updated_date": value.get("updated_date"),
                    "value_mw": value["value"]
                })
        
        errors = client.insert_rows_json(table_id, rows)
        if errors:
            raise Exception(f"BigQuery insert errors: {errors}")
        
        print(f"Inserted {len(rows)} rows into BigQuery")
        return len(rows)

    data = extract()
    load(data)

energy_pipeline()