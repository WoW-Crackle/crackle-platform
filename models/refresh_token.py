from datetime import datetime, timezone
from extensions import db

# Refresh Token 모델 정의
class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"

    # JWT refresh 토큰의 고유 식별자 (PK)
    jti = db.Column(db.String(64), primary_key=True)
    # 토큰 소유 사용자 ID (FK) 
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    # 토큰 무효화 여부 
    revoked = db.Column(db.Boolean, default=False, nullable=False)
    # refresh 토큰 발급 시각 (UTC)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    # refresh 토큰 만료 시각 (UTC)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # RefreshToken(N) : User(1) 관계
    user = db.relationship("User", backref=db.backref("refresh_tokens", lazy=True))