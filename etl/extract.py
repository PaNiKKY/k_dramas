from datetime import datetime
import os
import sys
import json
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraping_utils import get_all_links, get_drama_data, get_driver, get_last_page_number
from src.s3_utils import read_json_from_s3, write_json_to_s3

def get_last_page(url: str):
    driver = get_driver()
    last_page = get_last_page_number(url,driver)
    driver.quit()

    return last_page


def extract_data(title_links: list):
    # Initialize an empty list to store the drama data
    dramas = []
    error_links = ["start"]

    # Loop through each link and extract details
    while len(error_links) > 0:
        if "start" in error_links:
            error_links = []
            for link in tqdm(title_links, desc="Extracting data"):
                driver = get_driver()
                drama_dict, error_link = get_drama_data(link,driver)
                if error_link:
                    error_links.append(error_link)
                else:
                    dramas.append(drama_dict)
                driver.quit()
        else:
            for link in tqdm(error_links, desc="Retrying error pages"):
                driver = get_driver()
                drama_dict, error_link = get_drama_data(link,driver)
                if drama_dict:
                    dramas.append(drama_dict)
                    error_links.remove(link)
                driver.quit()
        # Create a drama object and append it to the list
    return dramas

def get_drama_links(start_year: int, end_year: int, bucket_name: str, folder_name: str) -> list:
    url = f"https://mydramalist.com/search?adv=titles&ty=68&co=3&re={start_year},{end_year}&so=date"
    last_page = get_last_page(url)
    pages = [url+f"&page={i}" for i in range(1, last_page+1)]
    title_links = get_all_links(pages)

    print(f"Number of dramas: {len(title_links)}")

    links_dict = {"links": title_links, "total": len(title_links)}

    write_json_to_s3(links_dict, bucket_name, folder_name, f"drama_links_{start_year}_{end_year}.json")

    return links_dict

if __name__ == "__main__":
    bucket_name = "k-dramas-bucket"
    folder_name = "raw"

    start_year = 2000
    end_year = 2014

    link_dict = read_json_from_s3(bucket_name, folder_name, f"drama_links_{start_year}_{end_year}.json")

    # print(link_dict)

    print(f"load from {start_year} to {end_year} total: {link_dict['total']}")
    details_list = extract_data(link_dict["links"])

    details_dict = {"dramas": details_list, "total": len(details_list), "date": datetime.now().strftime("%Y-%m-%d")}

    print(f"total dramas are scraped: {details_dict['total']}")

    write_json_to_s3(details_dict, bucket_name, folder_name+"/dramas_details", f"drama_details_{start_year}_{end_year}.json")

    print(f"drama details are saved to {bucket_name}/{folder_name}/drama_details_{start_year}_{end_year}.json")

