from flask import Flask, render_template
import config
from extensions import db, migrate

def create_app():
    app = Flask(__name__)

    # DB 연결 정보 (PostgreSQL) 
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    
    # SQLAlchemy 변경 추적 옵션 (사용 안 함 → 경고 제거용)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # JWT 서명/검증에 사용되는 서버 비밀키
    app.config["SECRET_KEY"] = config.SECRET_KEY

    # extensions.py에서 정의한 db, migrate 객체를 현재 app 인스턴스와 연결
    db.init_app(app)
    migrate.init_app(app, db)

    # 모델 import
    from models.user import User
    from models.category import Category
    from models.challenge import Challenge
    from models.submission import Submission
    from models.feedback import Feedback
    from models.refresh_token import RefreshToken

    # blueprint 등록
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from routes.challenges import challenges_bp
    app.register_blueprint(challenges_bp)

    # 라우트 정의
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/signup")
    def signup_page():
        return render_template("signup.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")
    
    @app.route("/challenges")
    def challenge_list_page():
        # 임시 문제 데이터
        challenges = [
            {
                "id": 1,
                "title": "SQL Injection",
                "info": "쿼리 조작을 통한 데이터베이스 공격",
                "tags": [{"name": "SQL", "color": "green"}]
            },
            {
                "id": 2,
                "title": "XSS",
                "info": "스크립트를 주입해 사용자 브라우저 공격",
                "tags": [{"name": "XSS", "color": "blue"}]
            },
            {
                "id": 3,
                "title": "파일 다운로드 취약점",
                "info": "임의 파일 다운로드를 통한 권한 탈취",
                "tags": [{"name": "파일", "color": "red"}]
            },
            {
                "id": 4,
                "title": "CSRF",
                "info": "사용자 인증 정보를 악용한 요청 위조",
                "tags": [{"name": "세션", "color": "blue"}]
            },
            {
                "id": 5,
                "title": "SSRF",
                "info": "서버 내부 요청을 유도해 내부 자원 접근",
                "tags": [{"name": "서버", "color": "green"}]
            }
        ]

        return render_template("challengelist.html", page="challenges", challenges=challenges)

    @app.route("/challenges/<int:challenge_id>")
    def challenge_detail(challenge_id):
        challenge_details = {
            1: {
                "title": "SQL Injection",
                "description": [
                    "이 문제는 일반적인 웹 애플리케이션에서 발견되는 SQL 인젝션 취약점을 다룹니다.",
                    "목표는 악의적인 SQL 쿼리를 주입하여 유효한 사용자 이름과 비밀번호 없이도 관리자 계정에 로그인하는 것입니다.",
                    "애플리케이션은 사용자 로그인에 `username`과 `password` 필드를 사용하며, 이 값들을 백엔드에서 적절한 입력 유효성 검사 없이 SQL 쿼리에 직접 연결합니다."
                ],
                "tasks": [
                    "웹 애플리케이션 로그인 페이지에서 SQL Injection 공격을 시도해보세요.",
                    "취약점을 악용하여 관리자 권한으로 로그인하십시오.",
                    "로그인 성공 후 표시되는 플래그를 확보하십시오."
                ],
                "icon": "🔒"
            },
            2: {
                "title": "XSS",
                "description": [
                    "입력값 검증 없이 페이지에 스크립트가 출력되는 취약점입니다.",
                    "사용자 입력이 그대로 렌더링되면 악성 스크립트 실행이 가능합니다."
                ],
                "tasks": [
                    "스크립트를 주입하여 경고창(alert)을 띄우세요.",
                    "다른 사용자의 세션 탈취 가능성을 분석하세요."
                ],
                "icon": "🧪"
            },
            3: {
                "title": "파일 다운로드 취약점",
                "description": [
                    "디렉토리 트래버설 취약점을 통한 민감 파일 유출 공격을 다룹니다.",
                    "백엔드에서 파일 경로를 검증하지 않으면 비정상적인 파일 접근이 가능합니다."
                ],
                "tasks": [
                    "`/etc/passwd` 또는 `app.py` 파일에 접근해보세요.",
                    "허용되지 않은 파일 다운로드 시도 결과를 확인하세요."
                ],
                "icon": "📂"
            },
            4: {
                "title": "CSRF",
                "description": [
                    "사용자의 의지와 상관없이 요청이 수행되는 취약점입니다.",
                    "보안 토큰 부족 또는 Referer 검증 미흡을 악용할 수 있습니다."
                ],
                "tasks": [
                    "전송 요청을 변조해보세요.",
                    "관리자 권한 변경과 같은 민감 요청 실행을 시도하세요."
                ],
                "icon": "🔗"
            },
            5: {
                "title": "SSRF",
                "description": [
                    "서버로 하여금 공격자가 원하는 주소로 요청을 보내게 하는 취약점입니다.",
                    "내부망 접근 또는 메타데이터 탈취가 가능합니다."
                ],
                "tasks": [
                    "localhost나 AWS 메타데이터(`169.254.169.254`)에 접근해보세요.",
                    "허용되지 않은 URL 접근 여부를 확인하세요."
                ],
                "icon": "🌐"
            }
        }

        challenge = challenge_details.get(challenge_id)
        if not challenge:
            return "Challenge Not Found", 404
        challenge["id"] = challenge_id
        return render_template("challengedetail.html", challenge=challenge)
    
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
            "total_count": 5,
            "pass_count": 2,
            "fail_count": 3,
            "hints": [
                "입력 유효성 검사를 강화하세요.",
                "SQL 인젝션 필터를 추가해보세요.",
                "보안 토큰을 사용하는 것을 고려하세요."
            ]
        }
        return render_template("testfeedback.html", **test_result)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)