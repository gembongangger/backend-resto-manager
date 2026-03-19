from flask import Blueprint, jsonify, request

from ..services.freeimage import upload_to_freeimage, UPLOAD_FOLDER

bp = Blueprint("upload", __name__)


@bp.post("/freeimage")
def upload_freeimage():
    image_file = None
    if request.files:
        image_file = request.files.get("image")

    url, error = upload_to_freeimage(image_file)
    if error or not url:
        return jsonify({"error": error or "upload_failed"}), 400

    return jsonify({"url": url})


@bp.get("/list")
def list_uploads():
    """Debug endpoint to list uploaded files"""
    import os
    
    if not os.path.exists(UPLOAD_FOLDER):
        return jsonify({"error": "upload_folder_not_found", "path": UPLOAD_FOLDER}), 404
    
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify({
        "folder": UPLOAD_FOLDER,
        "files": files,
        "count": len(files)
    })

