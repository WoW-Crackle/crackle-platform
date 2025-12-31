from datetime import datetime
from extensions import db


class Challenge(db.Model):
    __tablename__ = "challenges"

    # =========================
    # Columns
    # =========================
    id = db.Column(db.Integer, primary_key=True)

    # 개발 단계에서는 nullable=True (나중에 다시 False로 바꿔도 됨)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=True
    )

    title = db.Column(db.String(255), nullable=False)

    # 👉 한글 난이도 사용
    difficulty = db.Column(db.String(50), nullable=False)

    tags = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=False)

    vuln_type = db.Column(db.String(50), nullable=True)
    source_code = db.Column(db.Text, nullable=True)

    # JSON 문자열로 저장
    tasks = db.Column(db.Text, nullable=True)

    icon = db.Column(db.String(255), nullable=True)
    info = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =========================
    # Constraints
    # =========================
    __table_args__ = (
        db.CheckConstraint(
            "difficulty IN ('초급', '중급', '고급')",
            name="ck_challenges_difficulty"
        ),
    )

    # =========================
    # Relationships
    # =========================
    category = db.relationship(
        "Category",
        back_populates="challenges"
    )

    submissions = db.relationship(
        "Submission",
        back_populates="challenge",
        cascade="all, delete-orphan"
    )

    # =========================
    # Utils
    # =========================
    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "title": self.title,
            "difficulty": self.difficulty,
            "tags": self.tags,
            "description": self.description,
            "vuln_type": self.vuln_type,
            "source_code": self.source_code,
            "tasks": self.tasks,
            "icon": self.icon,
            "info": self.info,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Challenge {self.id} {self.title}>"
