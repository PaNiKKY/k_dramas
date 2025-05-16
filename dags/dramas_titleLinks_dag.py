from airflow.decorators import dag, task
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.extract import extract_data, get_drama_links

@dag(
    dag_id="dramas_links_dag",
    schedule="@monthly",
    start_date=datetime(2025, 4, 1),
    catchup=False,
)
def dramas_links_dag():

    @task
    def extract_drama_links_task(start_year: int, end_year: int):
        get_drama_links(start_year, end_year, "k-dramas-bucket", "raw")
        return f"Drama links for {start_year} to {end_year} extracted successfully."
    
    extract_drama_links_task(2000, 2025)

dramas_links_dag()