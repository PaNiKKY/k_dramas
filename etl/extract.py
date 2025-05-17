import os
import sys
import json
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraping_utils import get_all_links, get_drama_data, get_driver, get_last_page_number
from src.s3_utils import write_json_to_s3

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

# if __name__ == "__main__":
#     data = ['https://mydramalist.com/12010-wang-rungs-land', 'https://mydramalist.com/9951-shes-the-one', 'https://mydramalist.com/2868-honesty', 'https://mydramalist.com/15678-gibbs-family', 'https://mydramalist.com/9489-fireworks-2000', 'https://mydramalist.com/9737-three-friends', 'https://mydramalist.com/45859-my-funk-family', 'https://mydramalist.com/44757-nice-man', 'https://mydramalist.com/9221-look-back-in-anger', 'https://mydramalist.com/9643-bad-friends', 'https://mydramalist.com/6200-school-3', 'https://mydramalist.com/24060-fairy-commi', 'https://mydramalist.com/9016-legends-of-love', 'https://mydramalist.com/12601-say-it-with-your-eyes', 'https://mydramalist.com/9085-tough-guys-love', 'https://mydramalist.com/1123-emperor-wang-gun', 'https://mydramalist.com/12605-virtue', 'https://mydramalist.com/9736-because-of-you', 'https://mydramalist.com/12505-foolish-love', 'https://mydramalist.com/664-all-about-eve', 'https://mydramalist.com/5576-great-great', 'https://mydramalist.com/22951-soseol-mokminsimseo', 'https://mydramalist.com/9948-more-than-words-can-say', 'https://mydramalist.com/9813-more-than-love', 'https://mydramalist.com/1174-nonstop', 'https://mydramalist.com/1421-popcorn', 'https://mydramalist.com/12603-the-thiefs-daughter', 'https://mydramalist.com/9678-some-like-it-hot', 'https://mydramalist.com/2821-mr.-duke', 'https://mydramalist.com/12218-rna', 'https://mydramalist.com/9015-swat-police', 'https://mydramalist.com/1175-nonstop-2', 'https://mydramalist.com/15280-the-more-i-love-you', 'https://mydramalist.com/1209-secret-2000', 'https://mydramalist.com/1420-juliets-man', 'https://mydramalist.com/9641-the-full-sun', 'https://mydramalist.com/255-autumn-tale', 'https://mydramalist.com/12513-i-want-to-keep-seeing-you', 'https://mydramalist.com/12509-housewifes-rebellion', 'https://mydramalist.com/9635-foolish-princes', 'https://mydramalist.com/12507-golbangi', 'https://mydramalist.com/12597-roll-of-thunder', 'https://mydramalist.com/12517-pardon', 'https://mydramalist.com/12511-medical-center', 'https://mydramalist.com/12499-anger-of-angel', 'https://mydramalist.com/12595-tv-novel-promise', 'https://mydramalist.com/10091-mothers-and-sisters', 'https://mydramalist.com/7512-cheers-for-the-women', 'https://mydramalist.com/9814-snowflakes', 'https://mydramalist.com/45325-the-aspen-tree', 'https://mydramalist.com/2215-air-force', 'https://mydramalist.com/11656-the-golden-age-2000', 'https://mydramalist.com/12503-daddy-fish', 'https://mydramalist.com/12599-rookie', 'https://mydramalist.com/51723-why-can-t-we-stop-them', 'https://mydramalist.com/12629-still-love', 'https://mydramalist.com/12621-pretty-lady', 'https://mydramalist.com/12623-soon-ja', 'https://mydramalist.com/6347-ladies-of-the-palace', 'https://mydramalist.com/11201-tender-hearts', 'https://mydramalist.com/2290-delicious-proposal', 'https://mydramalist.com/7293-stock-flower', 'https://mydramalist.com/12617-morning-without-parting']
#     dramas = extract_data(data)
#     print(dramas)


