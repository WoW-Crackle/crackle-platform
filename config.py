import os
from dotenv import load_dotenv

load_dotenv()

# 환경 변수에서 DB 접속 정보 읽기 
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# SQLite를 사용하도록 데이터베이스 URI 변경
SQLALCHEMY_DATABASE_URI = "sqlite:///crackle.db"

# JWT 서명/검증에 사용되는 서버 비밀키
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

# SQLAlchemy의 객체 변경 감시 기능 비활성화
SQLALCHEMY_TRACK_MODIFICATIONS = False