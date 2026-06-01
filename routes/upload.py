import os
import uuid
from flask import Blueprint, request, jsonify

from utils.json_safe import json_error, parse_json_request, require_keys
from utils.validation import (
    DEFAULT_ALLOWED_EXTENSIONS,
    validate_upload_filename,
    validate_youtube_url,
)

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = DEFAULT_ALLOWED_EXTENSIONS
MAX_FILE_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 50 * 1024 * 1024))

def allowed_file(filename):
    return validate_upload_filename(filename, ALLOWED_EXTENSIONS)[1] is None

@upload_bp.route('/upload', methods=['POST'])
def upload():
    try:
        from tasks import process_upload

        session_id = str(uuid.uuid4())
        os.makedirs('uploads', exist_ok=True)

        if 'file' in request.files:
            file = request.files['file']
            filename, error = validate_upload_filename(file.filename, ALLOWED_EXTENSIONS)
            if error:
                return jsonify({"error": "upload_failed", "message": error}), 400

            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)
            if size > MAX_FILE_SIZE:
                return jsonify({"error": "upload_failed", "message": "File too large"}), 400

            original_filename = file.filename
            filepath = os.path.join('uploads', filename)
            file.save(filepath)
            title = filename

            task = process_upload.delay(session_id, filepath, title, original_filename)

        elif request.is_json:
            data, parse_error = parse_json_request(request)
            if parse_error:
                return json_error(parse_error)
            if require_keys(data, ["youtube_url"]):
                return jsonify({"error": "upload_failed", "message": "No file or youtube_url provided"}), 400

            url = data["youtube_url"]
            valid, error = validate_youtube_url(url)
            if not valid:
                return jsonify({"error": "upload_failed", "message": error}), 400

            title = f"YouTube Video ({url})"
            task = process_upload.delay(
                session_id, None, title, title, is_youtube=True, youtube_url=url
            )
        else:
            return jsonify({"error": "upload_failed", "message": "No file or youtube_url provided"}), 400

        return jsonify({
            "session_id": session_id,
            "task_id": task.id,
            "title": title,
            "status": "processing"
        }), 202

    except Exception as e:
        return jsonify({"error": "upload_failed", "message": str(e)}), 400
