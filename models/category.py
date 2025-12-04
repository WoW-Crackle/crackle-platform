from extensions import db

# Category 모델 정의 
class Category(db.Model):
    __tablename__ = "categories"
    
    # 카테고리 ID (PK) 
    id = db.Column(db.Integer, primary_key=True)
    # 카테고리 이름 
    name = db.Column(db.String(50), nullable=False, unique=True)
    # 카테고리 설명 
    description = db.Column(db.Text, nullable=True)
    
    # Category (1) : Challenge (N) 관계 설정
    challenges = db.relationship("Challenge", back_populates="category", cascade="all, delete-orphan")