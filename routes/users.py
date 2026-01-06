# routes/users.py

from flask import Blueprint, request, jsonify

users_bp = Blueprint("users", __name__)

@users_bp.route("/users/me", methods=["PATCH"])
def update_my_info():
    try:
        # 인증 체크 (지금은 토큰이 없다고 가정)
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({
                "code": "unauthorized",
                "message": "인증이 필요합니다."
            }), 401

        # 요청 데이터 받기
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")

        errors = {}

        # 유효성 검증
        if username and len(username) < 3:
            errors["username"] = ["허용되지 않는 닉네임입니다."]

        if email and "@" not in email:
            errors["email"] = ["올바른 이메일 형식이 아닙니다."]

        if errors:
            return jsonify({
                "code": "validation_error",
                "errors": errors
            }), 422

        # 중복 체크 (예시용)
        if username == "admin":
            return jsonify({
                "code": "duplicate",
                "errors": {
                    "username": ["이미 사용 중인 닉네임입니다."]
                }
            }), 409

        if email == "test@example.com":
            return jsonify({
                "code": "duplicate",
                "errors": {
                    "email": ["이미 사용 중인 이메일입니다."]
                }
            }), 409

        # 성공 응답
        return jsonify({
            "profile": {
                "username": username,
                "email": email
            }
        }), 200

    except Exception:
        # 서버 내부 오류
        return jsonify({
            "code": "internal_error",
            "message": "일시적인 오류가 발생했습니다."
        }), 500
