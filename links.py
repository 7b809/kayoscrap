import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import pymongo
import os

# MongoDB Atlas setup using GitHub secrets
mongo_url = os.getenv("MONGO_URL")  # Ensure MONGO_URL is set in GitHub Secrets
client = pymongo.MongoClient(mongo_url)
db = client["kayoanime"]
collection = db["links"]

base_url = "https://kayoanime.com"
visited_links = set()
max_depth = 1000  # Set the recursion depth limit
save_interval = 100  # Save count to print every 100 links

def save_links_to_mongodb(links):
    # Insert each unique link into the MongoDB collection
    documents = [{"url": link} for link in links]
    collection.insert_many(documents)
    print("\nSaved links to MongoDB.")

def get_links(url, depth=0):
    if depth > max_depth:
        save_links_to_mongodb(visited_links)  # Save links when max depth is reached
        return
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])  # Ensure absolute URL
            if link.startswith(base_url) and link not in visited_links:
                visited_links.add(link)

                # Print count for every 100 new links
                if len(visited_links) % save_interval == 0:
                    sys.stdout.write(f"\rTotal count: {len(visited_links)}")
                    sys.stdout.flush()

                # Recursively visit links, increment depth
                get_links(link, depth + 1)

    except requests.RequestException as e:
        print(f"\nFailed to access {url}: {e}")
        save_links_to_mongodb(visited_links)  # Save links on error

# Start scraping from the homepage
get_links(base_url)

# Print and save final count after recursion completes
print(f"\nFinal total count: {len(visited_links)}")
save_links_to_mongodb(visited_links)
