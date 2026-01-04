from flask import Flask, render_template, jsonify, abort, request
from flask_migrate import Migrate
import json
import os

from extensions import db
from models.challenge import Challenge
from models.user import User
from models.category import Category
from models.submission import Submission
from models.feedback import Feedback
from models.refresh_token import RefreshToken

from routes.auth import auth_bp

# =========================
# Flask 앱 생성
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder="templates",   # TemplateNotFound 방지
    static_folder="static"
)
# 개발용 JWT secret 하드코딩
app.config["SECRET_KEY"] = "supersecretkey"
# =========================
# DB 설정 (SQLite)
# =========================
db_path = os.path.join(BASE_DIR, "challenges.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

# =========================
# Blueprint 등록
# =========================
app.register_blueprint(auth_bp)

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
# 테스트용 DB 초기화 (⚠️ 수동 호출용)
# =========================
def init_db_with_sample_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        challenges = load_challenges()
        for c in challenges:
            challenge = Challenge(
                id=c["id"],
                title=c["title"],
                description=c["description",""],
                difficulty=c["difficulty"],
                tags=json.dumps(c.get("tags", []))
            )
            db.session.add(challenge)

        db.session.commit()
        print(f"{len(challenges)} challenges inserted into DB.")

# =========================
# 라우트 (페이지)
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
@app.route("/challenges")
def challenges_page():
    challenges = Challenge.query.all()

    for c in challenges:
        c.tags = json.loads(c.tags) if c.tags else []
    return render_template("challengelist.html", challenges=challenges)

# 문제 상세 페이지
@app.route("/challenges/page/<int:challenge_id>")
def challenge_detail_page(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    return render_template(
        "challengedetail.html",
        challenge=challenge,
        page="challenges"
    )

# 코드 수정 페이지
@app.route("/challenges/<int:challenge_id>/edit")
def challenge_edit(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    return render_template("codeedit.html", challenge=challenge)

# 피드백 페이지 (더미 데이터)
@app.route("/challenges/<int:cid>/feedback")
def show_feedback(cid):
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

# =========================
# API 라우트
# =========================
@app.route("/api/challenges")
def challenges_api():
    challenges = Challenge.query.all()
    return jsonify([c.to_dict() for c in challenges])

@app.route("/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if email == "test@example.com" and password == "password":
        return jsonify(
            access_token="example_access_token",
            refresh_token="example_refresh_token"
        ), 200

    return jsonify(message="Invalid credentials"), 401

# 디버깅용 데이터 출력
@app.route("/debug/challenges")
def debug_challenges():
    challenges = Challenge.query.all()
    return jsonify([c.to_dict() for c in challenges])

# 디버깅용 데이터 수정
@app.route("/debug/fix_challenges")
def fix_challenges():
    challenges = Challenge.query.filter(Challenge.description == None).all()
    for challenge in challenges:
        challenge.description = "기본 설명 텍스트"
        db.session.commit()
    return jsonify(message="빈 설명 필드가 수정되었습니다.")

# =========================
# 실행
# =========================
if __name__ == "__main__":
    app.run(debug=True)
