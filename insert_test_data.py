from extensions import db
from models.challenge import Challenge
from app import create_app  # Flask 애플리케이션 생성 함수 가져오기

# Flask 애플리케이션 컨텍스트 생성
app = create_app()
with app.app_context():
    # 예제 데이터 삽입
    challenge = Challenge(title="SQL Injection", difficulty="Medium", tags="SQL,Security")
    db.session.add(challenge)
    db.session.commit()
    print("Test data inserted successfully!")