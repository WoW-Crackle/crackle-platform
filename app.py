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

    # auth blueprint 등록
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

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

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)