import json
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from pymongo import MongoClient

# Load environment variables
mongodb_url = os.getenv("DROPBOX_ACCESS_TOKEN").split("_token_")[1]

# Connect to MongoDB
client = MongoClient(mongodb_url)
db = client['links_data']  # Database name
collection = db['link_lst']  # Collection name

data = []
link_lst = []
with open("data.json", 'r') as f:
    data = json.load(f)

# Set the path to chromedriver.exe
chrome_driver_path = r"chromedriver"

# Set up Chrome options
chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)

# Set up Chrome service
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Create a new instance of the Chrome webdriver
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

def get_soup(url):
    browser.get(url)
    time.sleep(2)
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

for index, entry in enumerate(data):
    print("index:", index, "-", len(data))
    if not entry['group_present']:
        for link in entry['links']:
            html_data = get_soup(link)
            # Select all elements with the `data-id` attribute
            elements = html_data.select('[data-id]')
            
            # Extract the `data-id` values and append them to the list
            data_id_list = [el['data-id'] for el in elements if 'data-id' in el.attrs]
            link_lst.append({
                "title": entry["folder_name"],
                "ids_lst": data_id_list
            })

# Insert the data into MongoDB
if link_lst:
    collection.insert_many(link_lst)
    print(f"Data successfully inserted into MongoDB collection: {collection.name}")
else:
    print("No data to insert.")

# Close the browser and MongoDB connection
browser.quit()
client.close()
