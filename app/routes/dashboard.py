from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models import Student


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/")
@login_required
def dashboard():
    """Display the main SmartAttend dashboard."""

    student_count = Student.query.count()

    return render_template(
        "dashboard.html",
        student_count=student_count,
        current_user=current_user
    )
