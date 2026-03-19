import os
import requests
from dotenv import load_dotenv

load_dotenv()

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")


def upload_image(file):
    if not file:
        return None

    if not IMGUR_CLIENT_ID:
        raise Exception("Imgur is not configured. Please set IMGUR_CLIENT_ID in .env")

    file_name = getattr(file, 'filename', 'image.jpg')
    
    # Read file content
    if hasattr(file, 'read'):
        file_content = file.read()
    else:
        file_content = file
    
    files = {
        'image': (file_name, file_content)
    }
    
    headers = {
        'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'
    }
    
    response = requests.post('https://api.imgur.com/3/image', headers=headers, files=files)
    
    if response.status_code != 200:
        raise Exception(f"Imgur upload failed: {response.json().get('data', {}).get('error', 'Unknown error')}")
    
    return response.json()['data']['link']
