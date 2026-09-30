from datetime import datetime

from app import db


class FaceEncoding(db.Model):
    __tablename__ = "face_encodings"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "students.id",
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    encoding = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    student = db.relationship(
        "Student",
        back_populates="face_encoding"
    )

    def __repr__(self):
        return f"<FaceEncoding student_id={self.student_id}>"
