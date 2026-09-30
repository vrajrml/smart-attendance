from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.forms.auth import LoginForm
from app.models import User


auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Display login page and authenticate the user."""

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()

        user = db.session.execute(
            db.select(User).where(
                User.username == username
            )
        ).scalar_one_or_none()

        if user is None or not user.check_password(form.password.data):
            flash(
                "Invalid username or password.",
                "danger"
            )

            return render_template(
                "login.html",
                form=form
            )

        login_user(user)

        flash(
            f"Welcome back, {user.username}!",
            "success"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    return render_template(
        "login.html",
        form=form
    )


@auth_bp.route("/logout")
@login_required
def logout():
    """Log the current user out."""

    logout_user()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )
