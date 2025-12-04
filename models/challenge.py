from datetime import datetime
from extensions import db

# Challenge 모델 정의 
class Challenge(db.Model):
    __tablename__ = "challenges"
    
    # 문제 ID (PK) 
    id = db.Column(db.Integer, primary_key=True)
    # 카테고리 ID (FK) 
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    # 문제 제목 
    title = db.Column(db.String(100), nullable=False)
    # 문제 설명 
    description = db.Column(db.Text, nullable=False)
    # 난이도: easy / medium / hard 중 하나
    difficulty = db.Column(db.String(20), nullable=False)
    # 취약점 유형: 예) SQLi, XSS, RCE 등
    vuln_type = db.Column(db.String(50), nullable=False)
    # 기본으로 제공되는 템플릿/취약 코드
    source_code = db.Column(db.Text, nullable=False)
    # 생성일시 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # 수정일시 
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # 테이블 레벨 제약조건 정의 : difficulty 컬럼은 정해진 값만 허용
    __table_args__ = (
        db.CheckConstraint(
            "difficulty IN ('easy','medium','hard')", name="ck_challenges_difficulty"
        ),
    )
    
    # Category(1) : Challenge(N) 관계 설정
    category = db.relationship("Category", back_populates="challenges")
    # Challenge(1) : Submission(N) 관계 설정 
    submissions = db.relationship("Submission", back_populates="challenge", cascade="all, delete-orphan")