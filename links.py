import requests
import pymongo
import os
import time
# MongoDB Atlas setup using GitHub secrets
mongo_url = os.getenv("MONGO_URL")  # Ensure MONGO_URL is set in GitHub Secrets
client = pymongo.MongoClient(mongo_url)
db = client["kayoanime"]
collection = db["links"]

# Loop through each page (from page 1 to the last page)
for page in range(1, 1104):  # Page 1 to 1103 (inclusive)
    
    url = f"https://api.jikan.moe/v4/anime?page={page}"
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Extract anime titles from the current page's response
        for idx, anime in enumerate(data['data']):
            title = anime['title']
            
            # Prepare the document to insert into MongoDB
            document = {f"title {len(list(collection.find())) + 1}": title}
            
            # Insert the document into the MongoDB collection
            collection.insert_one(document)
    else:
        print(f"Failed to retrieve data from page {page}. Status code: {response.status_code}")
    print(f"{page} out of {1104}")

print("Anime titles have been successfully inserted into MongoDB.")
