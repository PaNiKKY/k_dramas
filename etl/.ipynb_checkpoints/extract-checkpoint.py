import os
import sys
import json
from tqdm import tqdm
from typing import List, Dict, Optional
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraping_utils import get_all_links, get_drama_data, get_driver

def extract_data(url: str) -> list[dict]:

    driver = get_driver()
    title_links = get_all_links(url, driver)
    driver.quit()
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



if __name__ == "__main__":

    url = "https://mydramalist.com/search?adv=titles&ty=68&co=3&re=2025,2025&so=date"
    dramas = extract_data(url)
    with open("dramas.json", "w") as f:
        json.dump(dramas, f, indent=4)