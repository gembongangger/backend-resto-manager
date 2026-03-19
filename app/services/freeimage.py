import base64
import os
from typing import Optional, Tuple

import requests
from dotenv import load_dotenv

# Load .env file explicitly from PythonAnywhere path
load_dotenv("/home/gembonganggeredu/mysite/.env")

# Imgur API (works on PythonAnywhere)
IMGUR_API_URL = "https://api.imgur.com/3/image"
IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")

# FreeImage as fallback
FREEIMAGE_API_URL = "https://freeimage.host/api/1/upload"
FREEIMAGE_API_KEY = os.getenv("FREEIMAGE_API_KEY") or "6d207e02198a847aa98d0a2a901485a5"


def upload_to_freeimage(file) -> Tuple[Optional[str], Optional[str]]:
    """
    Upload image to Imgur (primary) or FreeImage (fallback).
    Imgur works on PythonAnywhere free tier.
    """
    if not file:
        return None, "no_file_provided"

    # Try Imgur first (works on PythonAnywhere)
    if IMGUR_CLIENT_ID:
        url, error = _upload_to_imgur(file)
        if url:
            return url, None

    # Fallback to FreeImage
    return _upload_to_freeimage_api(file)


def _upload_to_imgur(file) -> Tuple[Optional[str], Optional[str]]:
    """Upload to Imgur using anonymous API"""
    if not IMGUR_CLIENT_ID:
        return None, "missing_imgur_client_id"

    headers = {
        "Authorization": f"Client-ID {IMGUR_CLIENT_ID}",
    }

    # Read file and convert to base64
    if hasattr(file, "read"):
        file_content = file.read()
    else:
        file_content = file

    image_base64 = base64.b64encode(file_content).decode("utf-8")

    data = {
        "image": image_base64,
        "type": "base64",
    }

    try:
        response = requests.post(IMGUR_API_URL, headers=headers, data=data, timeout=20)
    except requests.RequestException as exc:
        return None, str(exc)

    if response.status_code != 200:
        try:
            payload = response.json()
            message = payload.get("data", {}).get("error") or payload.get("message")
        except Exception:
            message = response.text[:200]
        return None, message or f"imgur_http_{response.status_code}"

    try:
        payload = response.json()
    except ValueError:
        return None, "invalid_json_response"

    if not payload.get("success"):
        error_obj = payload.get("data", {}) or payload.get("error", {})
        message = error_obj.get("error") or "upload_failed"
        return None, message

    # Imgur returns image link
    data = payload.get("data") or {}
    url = data.get("link") or data.get("url")
    if not url:
        return None, "no_url_in_response"

    return url, None


def _upload_to_freeimage_api(file) -> Tuple[Optional[str], Optional[str]]:
    """Upload to freeimage.host API (fallback, may not work on PythonAnywhere)"""
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

