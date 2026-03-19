from flask import Blueprint, jsonify, request

from ..services.freeimage import upload_to_freeimage

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

