from flask import Blueprint, jsonify, request
from routes.store import session_store
from llm.generator import Generator
from agents.prompts import QUIZ_MCQ_PROMPT, QUIZ_SHORT_ANSWER_PROMPT
from agents.prompts import GRADING_PROMPT
from utils.json_helper import extract_json
from utils.json_safe import json_error, parse_json_request
from utils.validation import (
    validate_extracted_text,
    validate_quiz_count,
    validate_session_id,
)
from db import record_quiz_score

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz/<session_id>', methods=['GET'])
def get_quiz(session_id):
    valid, error = validate_session_id(session_id)
    if not valid:
        return json_error(error)
    if session_id not in session_store:
        return jsonify({"error": "not_found"}), 404
        
    quiz = session_store[session_id].get("quiz")
    if not quiz:
        return jsonify({"mcq": [], "short_answer": []})
    return jsonify(quiz)

@quiz_bp.route('/quiz/generate/<session_id>', methods=['POST'])
def generate_quiz(session_id):
    valid, error = validate_session_id(session_id)
    if not valid:
        return json_error(error)
    if session_id not in session_store:
        return jsonify({"error": "not_found"}), 404
        
    full_text = session_store[session_id].get("full_text", "")
    valid, error = validate_extracted_text(full_text, max_length=None)
    if not valid:
        return jsonify({"error": "no_text"}), 400
    full_text = full_text[:6000]
        
    data, parse_error = parse_json_request(request)
    if parse_error:
        return json_error(parse_error)
    difficulty = data.get('difficulty', 'medium')
    count, count_error = validate_quiz_count(data.get('count', 5))
    if count_error:
        return json_error(count_error)
    
    # We could adjust prompts based on difficulty and count, but for now we'll append to the prompt.
    custom_instruction = f" Ensure the difficulty is {difficulty}. Generate exactly {count} questions."
    
    generator = Generator(json_mode=True)
    try:
        def generate_json(prompt_template, text):
            try:
                prompt = prompt_template + custom_instruction
                res = generator.chain.invoke({"context": text, "question": prompt})
                from utils.json_helper import extract_json
                return extract_json(res)
            except Exception:
                pass
            return None

        mcq = generate_json(QUIZ_MCQ_PROMPT, full_text) or {"mcq": []}
        sa = generate_json(QUIZ_SHORT_ANSWER_PROMPT, full_text) or {"short_answer": []}
        
        for i, m in enumerate(mcq.get("mcq", [])):
            m["id"] = f"mcq_{i}"
            
        for i, s in enumerate(sa.get("short_answer", [])):
            s["id"] = f"sa_{i}"
            
        quiz = {"mcq": mcq.get("mcq", []), "short_answer": sa.get("short_answer", [])}
        session_data = session_store[session_id]
        session_data["quiz"] = quiz
        session_store[session_id] = session_data
        return jsonify(quiz)
    except Exception as e:
        return jsonify({"error": "generation_failed", "message": str(e)}), 500

@quiz_bp.route('/quiz/grade', methods=['POST'])
def grade_answer():
    data, parse_error = parse_json_request(request)
    if parse_error:
        return json_error(parse_error)
    question = data.get("question", "")
    user_answer = data.get("user_answer", "")
    sample_answer = data.get("sample_answer", "")
    session_id = data.get("session_id", "")
    if session_id:
        valid, error = validate_session_id(session_id)
        if not valid:
            return json_error(error)
    
    generator = Generator(json_mode=True)
    try:
        res = generator.chain.invoke({
            "context": f"Question: {question}\nSample Answer: {sample_answer}", 
            "question": GRADING_PROMPT.format(question=question, sample_answer=sample_answer, user_answer=user_answer)
        })
        grading = extract_json(res)
        if grading:
            if session_id and "score" in grading:
                record_quiz_score(session_id, grading["score"])
            return jsonify(grading)
    except Exception:
        pass
        
    # Fallback
    fallback = {
        "score": 5, 
        "feedback": "Unable to grade automatically. Please compare with sample answer.", 
        "correct_concepts": [], 
        "missed_concepts": [],
        "study_tip": "Review the sample answer and compare it against your response."
    }
    if session_id:
        record_quiz_score(session_id, fallback["score"])
    return jsonify(fallback)
