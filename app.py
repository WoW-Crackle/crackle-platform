from flask import Flask, render_template, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
import json
import os
from extensions import db

app = Flask(__name__)

# =========================
# DB 설정 (SQLite)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "challenges.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# =========================
# 샘플 데이터 로드 (개발용)
# =========================
def load_challenges():
    try:
        with open("static/script.js", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: static/script.js 파일 없음")
        return []
    except json.JSONDecodeError:
        abort(500, description="Challenge data JSON decode error")

# =========================
# 테스트용 DB 초기화
# =========================
def init_db_with_sample_data():
    db.drop_all()
    db.create_all()
    challenges = load_challenges()
    for c in challenges:
        challenge = Challenge(
            id=c["id"],
            title=c["title"],
            description=c["description"],
            difficulty=c["difficulty"],
            tags=json.dumps(c["tags"])
        )
        db.session.add(challenge)
    db.session.commit()
    print(f"{len(challenges)} challenges inserted into DB.")

# =========================
# 모델 import
# =========================
from models.user import User
from models.category import Category
from models.challenge import Challenge
from models.submission import Submission
from models.feedback import Feedback
from models.refresh_token import RefreshToken

from routes.auth import auth_bp
app.register_blueprint(auth_bp)

# =========================
# 라우트
# =========================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

# 문제 목록 페이지 (HTML)
# API: 전체 문제
@app.route("/challenges")
def get_challenges():
    challenges = Challenge.query.all()
    return jsonify([c.to_dict() for c in challenges])

# API: 문제 상세
@app.route("/challenges/page/<int:challenge_id>")
def challenge_detail_page(challenge_id):
    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        abort(404)
    return render_template("challengedetail.html", challenge=challenge, page="challenges")

@app.route("/challenges/<int:challenge_id>/edit")
def challenge_edit(challenge_id):
    # 간단히 제목만 매핑 (필요하면 난이도도 바꿔줘도 됨)
    title_map = {
        1: "SQL Injection",
        2: "XSS",
        3: "파일 다운로드 취약점",
        4: "CSRF",
        5: "SSRF",
    }
    title = title_map.get(challenge_id)
    if not title:
        return "Challenge Not Found", 404

    challenge = {
        "id": challenge_id,
        "title": title,
        "difficulty": "초급" if challenge_id in (1, 2) else "중급",
    }

    return render_template("codeedit.html", challenge=challenge)

@app.route("/challenges/<int:cid>/feedback")
def show_feedback(cid):
    # 테스트 결과 예시
    test_result = {
        "result": "fail",
        "pass_count": 2,
        "fail_count": 3,
        "hints": [
            "입력 유효성 검사를 강화하세요.",
            "SQL 인젝션 필터를 추가해보세요.",
            "보안 토큰을 사용하는 것을 고려하세요."
        ]
    }
    return render_template("testfeedback.html", **test_result)

@app.route("/submissions")
def submissions():
    return "내 제출 페이지 (구현 필요)"

@app.route("/dashboard")
def dashboard():
    return "대시보드 페이지 (구현 필요)"

@app.route("/auth/login", methods=["POST"])
def auth_login():
    from flask import request, jsonify

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Example validation logic
    if email == "test@example.com" and password == "password":
        return jsonify({
            "access_token": "example_access_token",
            "refresh_token": "example_refresh_token"
        }), 200

    return jsonify({"message": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(debug=True)