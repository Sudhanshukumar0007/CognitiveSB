import json

from flask import jsonify


def json_error(message, status=400):
    return jsonify({"success": False, "error": message}), status


def parse_json_fallback(raw_data):
    if not raw_data:
        return {}, None
    try:
        return json.loads(raw_data.decode("utf-8")), None
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "Invalid JSON payload"


def parse_json_request(request, default=None):
    default = {} if default is None else default
    if request.is_json:
        data = request.get_json(silent=True)
        if data is None:
            data, error = parse_json_fallback(request.get_data())
            if error:
                return None, error
        if not isinstance(data, dict):
            return None, "JSON payload must be an object"
        return data, None

    data, error = parse_json_fallback(request.get_data())
    if error:
        return None, error
    if data == {}:
        return default, None
    if not isinstance(data, dict):
        return None, "JSON payload must be an object"
    return data, None


def require_keys(data, keys):
    missing = [key for key in keys if key not in data]
    if missing:
        return f"Missing required field: {missing[0]}"
    return None
