from datetime import datetime
from zoneinfo import ZoneInfo

from app import db


IST = ZoneInfo("Asia/Kolkata")


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

    # Attendance finalization
    attendance_finalized = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    finalized_at = db.Column(
        db.DateTime,
        nullable=True
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

    @property
    def session_status(self):
        """
        Determine the current status of the class session
        using India Standard Time (Asia/Kolkata).

        Possible values:
        - upcoming
        - ongoing
        - ended
        """

        now = datetime.now(IST)

        session_start = datetime.combine(
            self.session_date,
            self.start_time,
            tzinfo=IST
        )

        session_end = datetime.combine(
            self.session_date,
            self.end_time,
            tzinfo=IST
        )

        if now < session_start:
            return "upcoming"

        if now < session_end:
            return "ongoing"

        return "ended"

    def __repr__(self):
        return (
            f"<ClassSession {self.id} "
            f"subject={self.subject_id} "
            f"date={self.session_date}>"
        )
