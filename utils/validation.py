import os
import re
from urllib.parse import urlparse

from werkzeug.utils import secure_filename


DEFAULT_ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "pptx"}
MAX_TEXT_LENGTH = 500000
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def validate_session_id(session_id):
    if not isinstance(session_id, str) or not SESSION_ID_RE.match(session_id):
        return False, "Invalid session_id"
    return True, None


def validate_quiz_count(count, default=5, minimum=1, maximum=20):
    if count in (None, ""):
        return default, None
    try:
        count = int(count)
    except (TypeError, ValueError):
        return None, "Quiz count must be a number"
    if count < minimum or count > maximum:
        return None, f"Quiz count must be between {minimum} and {maximum}"
    return count, None


def validate_flashcard_rating(value, field_name="rating", minimum=0, maximum=5):
    try:
        rating = int(value)
    except (TypeError, ValueError):
        return None, f"{field_name} must be a number"
    if rating < minimum or rating > maximum:
        return None, f"{field_name} must be between {minimum} and {maximum}"
    return rating, None


def validate_youtube_url(url):
    if not isinstance(url, str) or not url.strip():
        return False, "YouTube URL is required"

    url = url.strip()
    if "://" not in url:
        url = f"https://{url}"

    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    path = parsed.path or ""

    if parsed.scheme not in {"http", "https"}:
        return False, "Invalid YouTube URL"

    if host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if path == "/watch" and "v=" in parsed.query:
            return True, None
        if path.startswith(("/shorts/", "/embed/")) and len(path.split("/")) > 2:
            return True, None

    if host == "youtu.be" and path.strip("/"):
        return True, None

    return False, "Invalid YouTube URL"


def validate_upload_filename(filename, allowed_extensions=None):
    allowed_extensions = allowed_extensions or DEFAULT_ALLOWED_EXTENSIONS
    if not isinstance(filename, str) or not filename:
        return None, "No selected file"

    safe_name = secure_filename(filename)
    if not safe_name:
        return None, "Invalid filename"

    _, ext = os.path.splitext(safe_name)
    if not ext or ext[1:].lower() not in allowed_extensions:
        return None, "Invalid file type"

    return safe_name, None


def validate_extracted_text(text, max_length=MAX_TEXT_LENGTH):
    if not isinstance(text, str) or not text.strip():
        return False, "No text found for session"
    if max_length and len(text) > max_length:
        return False, "Extracted text is too large"
    return True, None
