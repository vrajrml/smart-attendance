from datetime import datetime

from app import db


class Attendance(db.Model):
    __tablename__ = "attendance"

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
        nullable=False
    )

    session_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "class_sessions.id",
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    status = db.Column(
        db.Enum("present", "late", "absent"),
        nullable=False,
        default="present"
    )

    marked_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    confidence = db.Column(
        db.Numeric(5, 4),
        nullable=True
    )

    student = db.relationship(
        "Student",
        back_populates="attendance_records"
    )

    session = db.relationship(
        "ClassSession",
        back_populates="attendance_records"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "session_id",
            name="uq_student_session"
        ),
    )

    def __repr__(self):
        return (
            f"<Attendance student={self.student_id} "
            f"session={self.session_id} "
            f"status={self.status}>"
        )
