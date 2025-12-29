from flask import Flask, render_template, jsonify, abort
import json

app = Flask(__name__)

# =========================
# 공통: 임시 데이터 로드
# (나중에 DB로 교체)
# =========================
def load_challenges():
    try:
        with open("static/script.js", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        abort(500, description="Challenge data JSON decode error")


# =========================
# 페이지 라우트 (HTML)
# =========================

# 홈
@app.route("/")
def home():
    return render_template("index.html", page="home")


# 문제 목록 페이지 (HTML)
@app.route("/challenges/page")
def challenge_list_page():
    challenges = load_challenges()
    return render_template(
        "challengelist.html",
        challenges=challenges,
        page="challenges"
    )


# 문제 상세 페이지 (HTML)
@app.route("/challenges/page/<int:challenge_id>")
def challenge_detail_page(challenge_id):
    challenges = load_challenges()
    challenge = next((c for c in challenges if c["id"] == challenge_id), None)

    if not challenge:
        abort(404)

    return render_template(
        "challengedetail.html",
        challenge=challenge,
        page="challenges"
    )


# =========================
# API 라우트 (명세 준수)
# =========================

# 문제 목록 조회 API
@app.route("/challenges", methods=["GET"])
def get_challenges():
    challenges = load_challenges()
    return jsonify(challenges)


# 문제 상세 조회 API
@app.route("/challenges/<int:challenge_id>", methods=["GET"])
def get_challenge_detail(challenge_id):
    challenges = load_challenges()
    challenge = next((c for c in challenges if c["id"] == challenge_id), None)

    if not challenge:
        abort(404)

    return jsonify(challenge)


# =========================
# 실행
# =========================
if __name__ == "__main__":
    app.run(debug=True)
