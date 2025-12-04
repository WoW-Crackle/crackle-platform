from datetime import datetime
from extensions import db

# User 모델 정의
class User(db.Model):
    __tablename__ = "users"
    
    # 사용자 ID (PK) 
    id = db.Column(db.Integer, primary_key=True)
    # 닉네임
    name = db.Column(db.String(50), nullable=False)
    # 이메일
    email = db.Column(db.String(100), nullable=False, unique=True)
    # 암호화된 비밀번호
    password = db.Column(db.String(255), nullable=False)
    # 권한 : user / admin
    role = db.Column(db.String(20), nullable=False, default="user")
    # 계정 생성 일시
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (
        db.CheckConstraint("role IN ('user','admin')", name="ck_users_role"),
    )
    
    # User(1) : Submission(N) 관계
    submissions = db.relationship("Submission", back_populates="user", cascade="all, delete-orphan")