from flask import Flask, render_template, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
import json
import os

app = Flask(__name__)

# =========================
# DB 설정 (SQLite)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "challenges.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =========================
# DB 모델
# =========================
class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.Text)  # JSON 문자열

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "tags": json.loads(self.tags) if self.tags else []
        }

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
# 라우트
# =========================

# 로그인 페이지
@app.route("/login")
def login_page():
    return render_template("login.html")

# 홈 페이지
@app.route("/")
def home():
    return render_template("index.html", page="home")

# 문제 목록 페이지 (HTML)
@app.route("/challenges/page")
def challenge_list_page():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    search = request.args.get("search", "").strip()
    difficulty = request.args.get("difficulty", "").strip()

    query = Challenge.query
    if search:
        query = query.filter(Challenge.title.contains(search))
    if difficulty:
        query = query.filter(Challenge.difficulty == difficulty)

    paginated = query.paginate(page=page, per_page=limit, error_out=False)
    challenges_list = [c.to_dict() for c in paginated.items]

    return render_template(
        "challengelist.html",
        challenges=challenges_list,
        page=page,
        limit=limit,
        total=paginated.total,
        page_name="challenges"
    )

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


# =========================
# 서버 실행
# =========================
if __name__ == "__main__":
    with app.app_context():
        init_db_with_sample_data()
    print("Starting Flask server at http://127.0.0.1:5000/")
    app.run(debug=True)
