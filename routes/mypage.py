from flask import Blueprint, request, jsonify

mypage_bp = Blueprint("mypage", __name__)

@mypage_bp.route("/users/me", methods=["GET"])
def get_my_page():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({
            "code": "unauthorized",
            "message": "인증이 필요합니다."
        }), 401

    return jsonify({
        "profile": {
            "user_id": 1,
            "username": "TestUser",
            "email": "test@example.com",
            "level": 1,
            "ranking": 999,
            "score_avg": 0,
            "created_at": "2025-01-01T00:00:00Z"
        },
        "progress": {
            "items": []
        },
        "settings": {
            "dark_mode": False
        }
    }), 200
