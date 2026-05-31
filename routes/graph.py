from flask import Blueprint, jsonify
from routes.store import session_store

graph_bp = Blueprint('graph', __name__)

@graph_bp.route('/graph/<session_id>', methods=['GET'])
def get_graph(session_id):
    if session_id not in session_store:
        return jsonify({"error": "not_found"}), 404
        
    graph_data = session_store[session_id].get("graph")
    if not graph_data:
        return jsonify({"nodes": [], "links": []})
        
    return jsonify(graph_data)

@graph_bp.route('/graph/generate/<session_id>', methods=['POST'])
def generate_graph(session_id):
    if session_id not in session_store:
        return jsonify({"error": "not_found"}), 404

    from tasks import generate_graph_task
    task = generate_graph_task.delay(session_id)
    return jsonify({"task_id": task.id, "status": "processing"}), 202
