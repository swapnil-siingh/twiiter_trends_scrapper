from selenium import webdriver
import sys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
import socket
import random
import uuid
import time
import datetime

CHROME_DRIVER_PATH = 'C:/Program Files/drivers/chromedriver-win64/chromedriver.exe'
# Set up MongoDB client
client = MongoClient("mongodb://localhost:27017/") 
db = client.twitter_scraper
collection = db.trends
# This is device ip address
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
def scrape_trending_topics(username, password):
    # ! Area Under Construction
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("--start-maximized")
    # Set up Selenium WebDriver
    driver = webdriver.Chrome(service=Service("C:/Program Files/drivers/chromedriver-win64/chromedriver.exe"))
    driver.maximize_window()
    try:
        # Twitter Login Page
        driver.get("https://x.com/i/flow/login")
        driver.implicitly_wait(10)
        
        # Log in
        username_field = driver.find_element(By.NAME, "text")
        username_field.send_keys(username)
        next_button = driver.find_element(By.XPATH, "//span[text()='Next']")
        next_button.click()
        
        driver.implicitly_wait(5)
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        login_button = driver.find_element(By.XPATH, "//span[text()='Log in']")
        login_button.click()

        # Wait for homepage to load and locate the "Show more" button
        driver.implicitly_wait(10)
        trending_now_section = driver.find_element(By.XPATH, "//div[@aria-label='Timeline: Trending now']")
        show_more_button = trending_now_section.find_element(By.TAG_NAME, "a")
        show_more_button.click()

    
        # Scrape "What's Happening" section
        driver.implicitly_wait(10)
        trends = driver.find_elements(By.CSS_SELECTOR, "div.css-146c3p1.r-bcqeeo.r-1ttztb7.r-qvutc0.r-37j5jr.r-a023e6.r-rjixqe.r-b88u0q.r-1bymd8e > span")
        trending_topics = []

        # Process the raw data
        for trend in trends:
            text = trend.text.strip()
            if text and "What's happening" not in text and "posts" not in text:
                trending_topics.append(text)

        # Remove duplicates while maintaining order
        trending_topics = list(dict.fromkeys(trending_topics))[:5]
        # Store data in MongoDB
        scraped_data = {
            "unique_id": str(uuid.uuid4()),
            "trends": trending_topics,
            "timestamp": datetime.datetime.now(),
            "ip_address": ip_address
            
        }
        collection.insert_one(scraped_data)
        print("Scraped Data:", scraped_data)
        return scraped_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        driver.quit()



if __name__ == "__main__":
    # Read username and password from command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python scraper.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    result=scrape_trending_topics(username, password)
    if result:
        print("Scraped Data:", result)
    else:
        print("Failed to scrape data.")
