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
    
    # @task
    # def extract_drama_links_task(start_year: int, end_year: int, bucket_name: str, folder_name: str):
    #     link_dict = get_drama_links(start_year, end_year, bucket_name, folder_name)
    #     return link_dict
    
    @task
    def load_drama_links_task(start_year: int, end_year: int, bucket_name: str, folder_name: str):
        link_dict = read_json_from_s3(bucket_name, folder_name, f"drama_links_{start_year}_{end_year}.json")
        print(link_dict['total'])
        return link_dict["links"]
    
    @task
    def sep_list(link: list, sep: int, i: int):
        sep = [(len(link)//sep)*i, (len(link)//sep)*(i+1)]
        if i == 2:
            sep[1] = len(link)
        return link[sep[0]:sep[1]]

    @task
    def extract_drama_details_task(link_dict: list, bucket_name: str, folder_name: str, strat_year: int, end_year: int, i: int):
        details_list = extract_data(link_dict)

        details_dict = {"dramas": details_list, "total": len(details_list), "date": datetime.now()}

        write_json_to_s3(details_dict, bucket_name, folder_name, f"drama_details_{strat_year}_{end_year}_{i}.json")

    link_dict = load_drama_links_task(2000, 2014, "k-dramas-bucket", "raw")
    for years in range(3):
        sep_link = sep_list(link_dict, 3, years)
        # link_dict = load_drama_links_task(years[0], years[1], "k-dramas-bucket", "raw")

        extract_drama_details_task(sep_link, "k-dramas-bucket", "raw", 2000, 2014, years)


dramas_detail_dag()