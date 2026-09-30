from datetime import datetime

from app import db


class ClassSession(db.Model):
    __tablename__ = "class_sessions"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "subjects.id",
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    session_date = db.Column(
        db.Date,
        nullable=False
    )

    start_time = db.Column(
        db.Time,
        nullable=False
    )

    end_time = db.Column(
        db.Time,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    subject = db.relationship(
        "Subject",
        back_populates="class_sessions"
    )

    attendance_records = db.relationship(
        "Attendance",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<ClassSession {self.id} "
            f"{self.session_date}>"
        )
