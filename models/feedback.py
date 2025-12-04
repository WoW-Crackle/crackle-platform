from datetime import datetime
from extensions import db

# Feedback 모델 정의
class Feedback(db.Model):
    __tablename__ = "feedbacks"
    
    # Feedback ID (PK)
    id = db.Column(db.Integer, primary_key=True)
    # 제출 ID (FK)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), nullable=False)
    # 피드백 내용 
    feedback_text = db.Column(db.Text, nullable=False)
    # 힌트 수준 : basic / detailed
    hint_level = db.Column(db.String(20), nullable=False, default="basic")
    # 생성 일시 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint(
            "hint_level IN ('basic','detailed')", name="ck_feedbacks_hint_level"
        ),
    )

    # Submission(1) : Feedback(N) 관계 설정
    submission = db.relationship("Submission", back_populates="feedbacks")