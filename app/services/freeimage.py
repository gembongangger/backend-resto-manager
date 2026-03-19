import os
from typing import Optional, Tuple

import requests
from dotenv import load_dotenv

# Load .env file explicitly from PythonAnywhere path
load_dotenv("/home/gembonganggeredu/mysite/.env")

FREEIMAGE_API_URL = "https://freeimage.host/api/1/upload"
FREEIMAGE_API_KEY = os.getenv("FREEIMAGE_API_KEY") or "6d207e02198a847aa98d0a2a901485a5"


def upload_to_freeimage(file) -> Tuple[Optional[str], Optional[str]]:
    if not file:
        return None, "no_file_provided"

    if not FREEIMAGE_API_KEY:
        return None, "missing_freeimage_api_key"

    file_name = getattr(file, "filename", "image.jpg")

    if hasattr(file, "read"):
        file_content = file.read()
    else:
        file_content = file

    data = {
        "key": FREEIMAGE_API_KEY,
        "action": "upload",
    }
    files = {
        "source": (file_name, file_content),
    }

    try:
        response = requests.post(FREEIMAGE_API_URL, data=data, files=files, timeout=20)
    except requests.RequestException as exc:
        return None, str(exc)

    if response.status_code != 200:
        try:
            payload = response.json()
            message = payload.get("error", {}).get("message") or payload.get("status_txt")
        except Exception:
            message = response.text[:200]
        return None, message or f"freeimage_http_{response.status_code}"

    try:
        payload = response.json()
    except ValueError:
        return None, "invalid_json_response"

    # FreeImageHost typically returns image url under image.url
    image = payload.get("image") or {}
    url = image.get("url") or image.get("url_viewer")
    if not url:
        error_obj = payload.get("error") or {}
        message = error_obj.get("message") or "upload_failed"
        return None, message

    return url, None

