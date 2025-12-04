import os
from dotenv import load_dotenv

load_dotenv()

# 환경 변수에서 DB 접속 정보 읽기 
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# 실제로 사용할 SQLAlchemy용 DB URI 문자열 생성 
SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# SQLAlchemy의 객체 변경 감시 기능 비활성화
SQLALCHEMY_TRACK_MODIFICATIONS = False