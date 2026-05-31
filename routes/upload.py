import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'pptx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload():
    try:
        from tasks import process_upload

        session_id = str(uuid.uuid4())
        os.makedirs('uploads', exist_ok=True)

        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "upload_failed", "message": "No selected file"}), 400
            if not allowed_file(file.filename):
                return jsonify({"error": "upload_failed", "message": "Invalid file type"}), 400

            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)
            if size > MAX_FILE_SIZE:
                return jsonify({"error": "upload_failed", "message": "File too large"}), 400

            filename = secure_filename(file.filename)
            original_filename = file.filename
            filepath = os.path.join('uploads', filename)
            file.save(filepath)
            title = filename

            task = process_upload.delay(session_id, filepath, title, original_filename)

        elif request.is_json and 'youtube_url' in request.json:
            url = request.json['youtube_url']
            if "youtube.com/watch" not in url and "youtu.be/" not in url:
                return jsonify({"error": "upload_failed", "message": "Invalid YouTube URL"}), 400

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
