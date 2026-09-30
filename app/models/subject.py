from datetime import datetime

from app import db


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    subject_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    subject_name = db.Column(
        db.String(100),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    class_sessions = db.relationship(
        "ClassSession",
        back_populates="subject",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Subject {self.subject_code} - {self.subject_name}>"
