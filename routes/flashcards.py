from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from routes.store import session_store
from db import (
    get_card_schedule,
    get_due_card_ids,
    update_card_schedule,
    upsert_card_schedule,
    upsert_flashcard_progress,
)

flashcards_bp = Blueprint('flashcards', __name__)

@flashcards_bp.route('/flashcards/<session_id>', methods=['GET'])
def get_flashcards(session_id):
    if session_id not in session_store:
        return jsonify({"error": "not_found"}), 404
        
    flashcards = session_store[session_id].get("flashcards")
    if not flashcards:
        return jsonify({"cards": []})
    cards = flashcards.get("cards", [])
    due_ids = get_due_card_ids(session_id)
    if due_ids:
        order = {card_id: idx for idx, card_id in enumerate(due_ids)}
        cards = sorted(cards, key=lambda card: order.get(card.get("id"), len(order)))
        flashcards = {**flashcards, "cards": cards}
    return jsonify(flashcards)

@flashcards_bp.route('/flashcards/generate/<session_id>', methods=['POST'])
def generate_flashcards(session_id):
    if session_id not in session_store:
        return jsonify({"error": "not_found"}), 404

    from tasks import generate_flashcards_task
    task = generate_flashcards_task.delay(session_id)
    return jsonify({"task_id": task.id, "status": "processing"}), 202

def sm2(easiness, interval, repetitions, quality):
    quality = max(0, min(5, int(quality)))
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * easiness)
        repetitions += 1
    easiness = max(1.3, easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    next_review = (datetime.utcnow() + timedelta(days=interval)).isoformat()
    return easiness, interval, repetitions, next_review

@flashcards_bp.route('/flashcards/rate', methods=['POST'])
def rate_flashcard():
    data = request.json or {}
    card_id = data.get("card_id")
    session_id = data.get("session_id")
    mastery = data.get("mastery", 1)
    quality = data.get("quality", mastery)
    
    if session_id not in session_store:
        return jsonify({"error": "not_found"}), 404
        
    cards = session_store[session_id].get("flashcards", {}).get("cards", [])
    
    for card in cards:
        if card.get("id") == card_id:
            schedule = get_card_schedule(card_id)
            if not schedule:
                upsert_card_schedule(session_id, card_id, card.get("front", ""), datetime.utcnow().isoformat())
                schedule = get_card_schedule(card_id)

            easiness, interval, repetitions, next_review = sm2(
                schedule["easiness"],
                schedule["interval"],
                schedule["repetitions"],
                quality,
            )
            update_card_schedule(card_id, easiness, interval, repetitions, next_review)
            card["mastery"] = mastery
            card["next_review"] = next_review
            session_data = session_store[session_id]
            session_data["flashcards"] = {"cards": cards}
            session_store[session_id] = session_data
            mastered = sum(1 for c in cards if c.get("mastery", 0) >= 3)
            upsert_flashcard_progress(session_id, len(cards), mastered)
            
            return jsonify({
                "card_id": card_id,
                "next_review": next_review,
                "interval_days": interval
            })
            
    return jsonify({"error": "card_not_found"}), 404
