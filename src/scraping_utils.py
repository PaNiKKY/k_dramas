from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
from tqdm import tqdm
from pydantic import BaseModel
from typing import List, Optional, Dict
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument(f'--user-agent={user_agent}')
    options.add_experimental_option("detach", True)
    # options.add_argument("--window-size=1920,1080")
    # options.add_argument("--start-maximized")

    # driver = webdriver.Chrome(options=options)

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    return driver

class drama(BaseModel):
    title: str
    rating_list: List[str]
    synopsis: Optional[str] = None
    details: Optional[str] = None
    episodes: List[str]
    cast: Dict[str, str]
    reviews: Optional[List[str]] = None

def get_title_links(page_url, driver):
    title_list = []
    error_page = ""
    try:
        driver.get(page_url)
        time.sleep(3)
    except Exception as e:
        print(f"Error: {page_url}")
        error_page = page_url
    else:
        all_title = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "h6"))
        )
        for title in all_title:
            title_list.append(title.find_element(By.TAG_NAME, "a").get_attribute("href"))
    finally:
        return title_list, error_page

def get_last_page_number(url, driver):
    driver.get(url)
    time.sleep(3)

    last_page_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
    ).find_element(By.CLASS_NAME, "last").find_element(By.TAG_NAME, "a").get_attribute("href")

    last_page = int(last_page_link.split("=")[-1])
    print(f"Last page: {last_page}")
    return last_page

def get_all_links(url_list) -> list:

    title_links = []
    error_links = ["strat"]

    while len(error_links) > 0:
        if "strat" in error_links:
            error_links = []
            for page_url in tqdm(url_list, desc="Getting title links"):
                # page_url = url + f"&page={i}"
                driver = get_driver()
                title_link, error_link = get_title_links(page_url,driver)
                title_links.extend(title_link)
                if error_link == page_url:
                    error_links.append(error_link)
                driver.quit()
        else:
            for page_url in tqdm(error_links, desc="Retrying error pages"):
                driver = get_driver()
                title_link, error_link = get_title_links(page_url,driver)
                if error_link != page_url:
                    title_links.extend(title_link)
                    error_links.remove(page_url)
                driver.quit()
    return title_links

def get_details(url, driver):
    try:
        title = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            ).text

        reviews = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "hfs"))
            )
        rating_list = [review.text for review in reviews]

        synopsis_pre = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "show-synopsis"))
            ).text

        synopsis = synopsis_pre.split("Edit Translation")[0]

        details = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "show-detailsxss"))
        ).text
    except Exception as e:
        print(f"Error at details: {url}")
        error = url
        return None, None, None, None, error
    else:
        return title, rating_list, synopsis, details, None
        

def get_episode(url, nav_button, driver):
    try:
        nav_button.click()
        time.sleep(1)

        nav_bars = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nav-tabs"))
        ).find_elements(By.TAG_NAME, "li")[2]

        episodes = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "episodes"))
            ).find_elements(By.CLASS_NAME, "episode")

        episodes = [episode.text for episode in episodes]
    except Exception as e:
        print(f"Error at episodes: {url}")
        error = url
        return None, error, None
    else:
        return episodes, None, nav_bars

def get_cast(url, nav_button, driver):
    try:
        nav_button.click()
        time.sleep(1)

        nav_bars = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nav-tabs"))
        ).find_elements(By.TAG_NAME, "li")[3]

        casts = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cast-credits"))
            ).find_element(By.CLASS_NAME, "box-body")
        cast_title = [title.text for title in casts.find_elements(By.TAG_NAME, "h3")]
        cast_names = [name.text for name in casts.find_elements(By.TAG_NAME, "ul")]

        if len(cast_title) != len(cast_names):
            print("Error: cast title and name length mismatch")
            cast_list = []
        else:
            cast_list = {cast_title[i]: cast_names[i] for i in range(len(cast_title))}  
    except Exception as e:
        print(f"Error at cast: {url}")
        error = url
        return None, error, None
    else:
        return cast_list, None, nav_bars

def get_reviews(url, nav_button, driver):
    try:
        nav_button.click()
        time.sleep(1)
        try:
            get_header = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "container-fluid"))
            ).find_element(By.CLASS_NAME, "box").find_elements(By.CLASS_NAME, "review")
        except:
            reviews = []
        else:
            reviews = [review.text for review in get_header]
    except Exception as e:
        print(f"Error at reviews: {url}")
        error = url
        return None, error
    else:
        return reviews, None
    
def get_drama_data(url, driver):
    try:
        driver.get(url)
        time.sleep(1)
        # driver.save_screenshot("screenshot.png")
        nav_bars = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nav-tabs"))
        ).find_elements(By.TAG_NAME, "li")
    except Exception as e:
        print(f"Error at link: {url}")
        error = url
        return None, error
    else:
        title, rating_list, synopsis, details,error_details = get_details(url, driver)
        episodes, error_episodes, nav_cast = get_episode(url, nav_bars[1], driver)
        cast, error_cast, nav_review = get_cast(url, nav_cast, driver)
        reviews, error_reviews = get_reviews(url, nav_review, driver)

        if error_details or error_episodes or error_cast or error_reviews:
            error = url
            return None, error
        else:
            drama_obj = drama(
                title=title,
                rating_list=rating_list,
                synopsis=synopsis,
                details=details,
                episodes=episodes,
                cast=cast,
                reviews=reviews
            )
            return drama_obj.dict(), None

    

    