from datetime import datetime
from extensions import db

# Submission 모델 정의
class Submission(db.Model):
    __tablename__ = "submissions"
    
    # 제출 ID (PK)
    id = db.Column(db.Integer, primary_key=True)
    # 제출한 사용자 ID (FK)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # 제출한 문제 ID (FK)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    # 제출된 코드 내용
    submitted_code = db.Column(db.Text, nullable=False)
    # 제출 상태: pending / running / passed / failed
    status = db.Column(db.String(20), nullable=False, default="pending")
    # 채점 점수
    score = db.Column(db.Integer, nullable=True)
    # 제출 일시 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('pending','running','passed','failed')",
            name="ck_submissions_status",
        ),
    )

    # User(1) : Submission(N) 관계 설정
    user = db.relationship("User", back_populates="submissions")
    
    # Challenge(1) : Submission(N) 관계 설정
    challenge = db.relationship("Challenge", back_populates="submissions")
    
    # Submission(1) : Feedback(N) 관계 설정 
    feedbacks = db.relationship("Feedback", back_populates="submission", cascade="all, delete-orphan")