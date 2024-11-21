import dropbox
import os
from pymongo import MongoClient
from getfiles import download_file_from_drive
from getaudio import get_audio_streams, extract_audio

# Dropbox Access Token
token_url = os.getenv("DROPBOX_ACCESS_TOKEN").split("_token_")
ACCESS_TOKEN = token_url[0]
DROPBOX_FOLDER = "/getdata101"  # Folder name in your Dropbox App

# MongoDB setup
client = MongoClient(token_url[0])
db = client['links_data']  # Database name
links_collection = db['links_collection']  # Collection name

# Function to upload file to Dropbox
def upload_to_dropbox(local_file_path, dropbox_file_path):
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    
    with open(local_file_path, 'rb') as f:
        try:
            # Upload the file
            dbx.files_upload(f.read(), dropbox_file_path, mute=True)
            print(f"Uploaded {local_file_path} to Dropbox at {dropbox_file_path}")
        except dropbox.exceptions.ApiError as e:
            print(f"Failed to upload {local_file_path}: {e}")

# Function to check and update MongoDB document flags
def update_mongodb_flags(drive_url):
    link_doc = links_collection.find_one({"link": drive_url})
    
    if link_doc:
        # If processing is complete, update exit_flag to True
        links_collection.update_one(
            {"link": drive_url},
            {"$set": {"exit_flag": True}}
        )
        print(f"Processed {drive_url}, updated exit_flag.")
        return True  # Continue processing
    return False  # No link found to process

def main(drive_url):
    # Step 1: Download the file from Google Drive
    downloaded_file_name = download_file_from_drive(drive_url)
    
    if downloaded_file_name:
        print(f"Downloaded file: {downloaded_file_name}")
        
        # Step 2: Extract audio streams from the downloaded file
        audio_streams = get_audio_streams(downloaded_file_name)
        
        # Step 3: Extract and save audio files
        extract_audio(downloaded_file_name, audio_streams)
        
        # Step 4: Upload audio files to Dropbox
        for audio_file in os.listdir():
            if audio_file.endswith('.mp3'):  # Upload only the .mp3 files
                local_file_path = os.path.join(os.getcwd(), audio_file)
                dropbox_file_path = os.path.join(DROPBOX_FOLDER, audio_file)
                upload_to_dropbox(local_file_path, dropbox_file_path)
        
        # Step 5: Update MongoDB exit_flag to True after processing
        if update_mongodb_flags(drive_url):
            print("Processing complete, moving to the next link.")
    else:
        print("File download failed.")

if __name__ == "__main__":
    # Fetch the link from MongoDB where new_links = True and exit_flag = False
    link_doc = links_collection.find_one()  # Assuming you want the first document

    drive_url = link_doc['link']  # Extract the drive URL from the document
    print(f"Processing link: {drive_url}")
        
    # Call the main function with the fetched drive URL
    main(drive_url)
    
