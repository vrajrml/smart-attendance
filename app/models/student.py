from datetime import datetime

from app import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    roll_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=True
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    department = db.Column(
        db.String(100),
        nullable=True
    )

    semester = db.Column(
        db.Integer,
        nullable=True
    )

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

    face_encoding = db.relationship(
        "FaceEncoding",
        back_populates="student",
        uselist=False,
        cascade="all, delete-orphan"
    )

    attendance_records = db.relationship(
        "Attendance",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Student {self.roll_number} - {self.name}>"
