from airflow.decorators import dag, task
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.extract import extract_data, get_drama_links
from src.s3_utils import read_json_from_s3, write_json_to_s3

@dag(
    dag_id="dramas_detail_dag",
    schedule="@monthly",
    start_date=datetime(2025, 4, 1),
    catchup=False,
)
def dramas_detail_dag():
    @task
    def load_drama_links_task(start_year: int, end_year: int, bucket_name: str, folder_name: str):
        link_dict = read_json_from_s3(bucket_name, folder_name, f"drama_links_{start_year}_{end_year}.json")
        # print(link_dict)
        return link_dict

    @task
    def extract_drama_details_task(link_dict: dict):
        details_list = extract_data(link_dict["links"])

        details_dict = {"dramas": details_list, "total": len(details_list), "date": datetime.now()}

        write_json_to_s3(details_dict, "k-dramas-bucket", "raw", f"drama_details_2020_2025.json")
        

    link_dict = load_drama_links_task(2000, 2025, "k-dramas-bucket", "raw")

    extract_drama_details_task(link_dict)


dramas_detail_dag()