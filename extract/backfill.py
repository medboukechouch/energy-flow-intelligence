from datetime import datetime, timedelta
from rte_client import get_token, get_production_data_for_date
from google.cloud import bigquery
import time

def backfill_historical_data(days=30):
    """
    Fetch and load historical data for the last N days into BigQuery.
    """
    client = bigquery.Client(project="project-da2d9305-97cf-4aec-9f3")
    table_id = "project-da2d9305-97cf-4aec-9f3.energy_data.production_by_type"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema=[
            bigquery.SchemaField("production_type", "STRING"),
            bigquery.SchemaField("start_date", "TIMESTAMP"),
            bigquery.SchemaField("end_date", "TIMESTAMP"),
            bigquery.SchemaField("updated_date", "TIMESTAMP"),
            bigquery.SchemaField("value_mw", "INTEGER"),
        ]
    )
    
    token = get_token()
    today = datetime.today()
    
    for i in range(1, days + 1):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        print(f"Fetching data for {date_str}...")
        
        try:
            data = get_production_data_for_date(token, date_str)
            
            rows = []
            for item in data.get("actual_generations_per_production_type", []):
                production_type = item["production_type"]
                for value in item["values"]:
                    rows.append({
                        "production_type": production_type,
                        "start_date": value["start_date"],
                        "end_date": value["end_date"],
                        "updated_date": value.get("updated_date"),
                        "value_mw": value["value"]
                    })
            
            if rows:
                job = client.load_table_from_json(rows, table_id, job_config=job_config)
                job.result()
                print(f"✅ {date_str}: inserted {len(rows)} rows")
            else:
                print(f"⚠️ {date_str}: no data returned")
                
        except Exception as e:
            print(f"❌ {date_str}: error — {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    backfill_historical_data(days=30)