from datetime import datetime
from extensions import db

class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)  # 기본 키
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)  # 외래 키
    title = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=False)
    vuln_type = db.Column(db.String(50), nullable=False)
    source_code = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.CheckConstraint("LOWER(difficulty) IN ('easy','medium','hard')", name="ck_challenges_difficulty"),
    )

    # Category(1) : Challenge(N) 관계 설정
    category = db.relationship("Category", back_populates="challenges")
    # Challenge(1) : Submission(N) 관계 설정 
    submissions = db.relationship("Submission", back_populates="challenge", cascade="all, delete-orphan")