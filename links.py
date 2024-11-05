import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

base_url = "https://kayoanime.com"
visited_links = set()
max_depth = 1000  # Set the recursion depth limit

def get_links(url, depth=0):
    if depth > max_depth:
        return  # Stop recursion if depth limit is reached
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all 'a' tags with href attributes
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])  # Ensure absolute URL
            if link.startswith(base_url) and link not in visited_links:
                visited_links.add(link)
                
                # Clear previous total count line and print the updated count
                sys.stdout.write(f"\rTotal count: {len(visited_links)}")
                sys.stdout.flush()

                # Recursively visit links, increment depth
                get_links(link, depth + 1)

    except requests.RequestException as e:
        print(f"\nFailed to access {url}: {e}")

# Start scraping from the homepage
get_links(base_url)

# Print final total count after recursion finishes
print(f"\nFinal total count: {len(visited_links)}")
