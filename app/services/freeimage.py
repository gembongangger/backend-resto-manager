import os
import uuid
from typing import Optional, Tuple

from dotenv import load_dotenv

# Load .env file explicitly from PythonAnywhere path
load_dotenv("/home/gembonganggeredu/mysite/.env")

# Local upload folder for PythonAnywhere
UPLOAD_FOLDER = "/home/gembonganggeredu/mysite/static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_to_freeimage(file) -> Tuple[Optional[str], Optional[str]]:
    """
    Upload image to local server folder.
    Returns URL path relative to static folder.
    """
    if not file:
        return None, "no_file_provided"

    # Check file size
    if hasattr(file, "seek") and hasattr(file, "tell"):
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        if file_size > MAX_FILE_SIZE:
            return None, "file_too_large"

    if not hasattr(file, "filename"):
        return None, "invalid_file_object"

    filename = file.filename
    if not filename:
        return None, "no_filename"

    if not allowed_file(filename):
        return None, "file_type_not_allowed"

    # Generate unique filename
    ext = filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)

    # Return URL path (relative to static folder)
    url = f"/static/uploads/{unique_filename}"
    return url, None

