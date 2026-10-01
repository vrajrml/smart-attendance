from datetime import date

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app import db
from app.models import Attendance, ClassSession, Student


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/")
@login_required
def dashboard():
    """Display the SmartAttend dashboard."""

    # ---------------------------------------------------------
    # TOTAL STUDENTS
    # ---------------------------------------------------------

    student_count = db.session.execute(
        db.select(db.func.count(Student.id))
    ).scalar_one()


    # ---------------------------------------------------------
    # TODAY'S CLASS SESSIONS
    # ---------------------------------------------------------

    today = date.today()

    today_sessions = db.session.execute(
        db.select(ClassSession).where(
            ClassSession.session_date == today
        )
    ).scalars().all()


    # ---------------------------------------------------------
    # TODAY'S ATTENDANCE
    # ---------------------------------------------------------

    session_ids = [
        session.id
        for session in today_sessions
    ]

    attendance_records = []

    if session_ids:

        attendance_records = db.session.execute(
            db.select(Attendance).where(
                Attendance.session_id.in_(session_ids)
            )
        ).scalars().all()


    # ---------------------------------------------------------
    # PRESENT / LATE COUNT
    # ---------------------------------------------------------

    present_today = sum(
        1
        for record in attendance_records
        if record.status in ("present", "late")
    )


    # ---------------------------------------------------------
    # EXPECTED ATTENDANCE
    # ---------------------------------------------------------

    expected_attendance = (
        student_count * len(today_sessions)
    )


    # ---------------------------------------------------------
    # ABSENT / UNMARKED COUNT
    # ---------------------------------------------------------

    absent_today = max(
        expected_attendance - present_today,
        0
    )


    # ---------------------------------------------------------
    # ATTENDANCE RATE
    # ---------------------------------------------------------

    if expected_attendance > 0:

        attendance_rate = round(
            (
                present_today
                / expected_attendance
            ) * 100,
            1
        )

    else:

        attendance_rate = 0


    # ---------------------------------------------------------
    # RENDER DASHBOARD
    # ---------------------------------------------------------

    return render_template(
        "dashboard.html",
        student_count=student_count,
        present_today=present_today,
        absent_today=absent_today,
        attendance_rate=attendance_rate,
        current_user=current_user
    )
