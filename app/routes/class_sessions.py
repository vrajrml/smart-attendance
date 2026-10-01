from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)
from flask_login import login_required

from app import db
from app.forms.class_session import (
    ClassSessionForm,
    DeleteClassSessionForm
)
from app.models import ClassSession, Subject


class_sessions_bp = Blueprint(
    "class_sessions",
    __name__,
    url_prefix="/class-sessions"
)


def load_subject_choices(form):
    """Load all subjects into the session form."""

    subjects = db.session.execute(
        db.select(Subject).order_by(
            Subject.subject_code
        )
    ).scalars().all()

    form.subject_id.choices = [
        (
            subject.id,
            f"{subject.subject_code} - {subject.subject_name}"
        )
        for subject in subjects
    ]

    return subjects


@class_sessions_bp.route("/")
@login_required
def list_sessions():
    """Display all class sessions."""

    search = request.args.get(
        "search",
        ""
    ).strip()

    query = (
        db.select(ClassSession)
        .join(Subject)
    )

    if search:

        search_pattern = f"%{search}%"

        query = query.where(
            db.or_(
                Subject.subject_code.ilike(
                    search_pattern
                ),
                Subject.subject_name.ilike(
                    search_pattern
                )
            )
        )

    query = query.order_by(
        ClassSession.session_date.desc(),
        ClassSession.start_time.desc()
    )

    sessions = db.session.execute(
        query
    ).scalars().all()

    delete_form = DeleteClassSessionForm()

    return render_template(
        "class_sessions/list.html",
        sessions=sessions,
        search=search,
        delete_form=delete_form
    )


@class_sessions_bp.route(
    "/add",
    methods=["GET", "POST"]
)
@login_required
def add_session():
    """Create a new class session."""

    form = ClassSessionForm()

    subjects = load_subject_choices(form)

    if not subjects:

        flash(
            "Please create a subject before creating a class session.",
            "warning"
        )

        return redirect(
            url_for(
                "subjects.add_subject"
            )
        )

    if form.validate_on_submit():

        if form.end_time.data <= form.start_time.data:

            flash(
                "End time must be later than start time.",
                "danger"
            )

            return render_template(
                "class_sessions/add.html",
                form=form
            )

        existing_session = db.session.execute(
            db.select(ClassSession).where(
                ClassSession.subject_id == form.subject_id.data,
                ClassSession.session_date == form.session_date.data,
                ClassSession.start_time == form.start_time.data,
                ClassSession.end_time == form.end_time.data
            )
        ).scalar_one_or_none()

        if existing_session:

            flash(
                "An identical class session already exists.",
                "danger"
            )

            return render_template(
                "class_sessions/add.html",
                form=form
            )

        session = ClassSession(
            subject_id=form.subject_id.data,
            session_date=form.session_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data
        )

        db.session.add(session)
        db.session.commit()

        flash(
            "Class session created successfully.",
            "success"
        )

        return redirect(
            url_for(
                "class_sessions.list_sessions"
            )
        )

    return render_template(
        "class_sessions/add.html",
        form=form
    )


@class_sessions_bp.route(
    "/<int:session_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_session(session_id):
    """Edit an existing class session."""

    session = db.get_or_404(
        ClassSession,
        session_id
    )

    form = ClassSessionForm(
        obj=session
    )

    load_subject_choices(form)

    if form.validate_on_submit():

        if form.end_time.data <= form.start_time.data:

            flash(
                "End time must be later than start time.",
                "danger"
            )

            return render_template(
                "class_sessions/edit.html",
                form=form,
                session=session
            )

        existing_session = db.session.execute(
            db.select(ClassSession).where(
                ClassSession.subject_id == form.subject_id.data,
                ClassSession.session_date == form.session_date.data,
                ClassSession.start_time == form.start_time.data,
                ClassSession.end_time == form.end_time.data,
                ClassSession.id != session.id
            )
        ).scalar_one_or_none()

        if existing_session:

            flash(
                "An identical class session already exists.",
                "danger"
            )

            return render_template(
                "class_sessions/edit.html",
                form=form,
                session=session
            )

        session.subject_id = form.subject_id.data
        session.session_date = form.session_date.data
        session.start_time = form.start_time.data
        session.end_time = form.end_time.data

        db.session.commit()

        flash(
            "Class session updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "class_sessions.list_sessions"
            )
        )

    return render_template(
        "class_sessions/edit.html",
        form=form,
        session=session
    )


@class_sessions_bp.route(
    "/<int:session_id>/delete",
    methods=["POST"]
)
@login_required
def delete_session(session_id):
    """Delete a class session."""

    session = db.get_or_404(
        ClassSession,
        session_id
    )

    form = DeleteClassSessionForm()

    if not form.validate_on_submit():

        flash(
            "Invalid delete request.",
            "danger"
        )

        return redirect(
            url_for(
                "class_sessions.list_sessions"
            )
        )

    db.session.delete(session)
    db.session.commit()

    flash(
        "Class session deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "class_sessions.list_sessions"
        )
    )
