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
from app.forms.subject import DeleteSubjectForm, SubjectForm
from app.models import Subject


subjects_bp = Blueprint(
    "subjects",
    __name__,
    url_prefix="/subjects"
)


@subjects_bp.route("/")
@login_required
def list_subjects():
    """Display all subjects."""

    search = request.args.get(
        "search",
        ""
    ).strip()

    query = db.select(Subject)

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
        Subject.subject_code
    )

    subjects = db.session.execute(
        query
    ).scalars().all()

    delete_form = DeleteSubjectForm()

    return render_template(
        "subjects/list.html",
        subjects=subjects,
        search=search,
        delete_form=delete_form
    )


@subjects_bp.route(
    "/add",
    methods=["GET", "POST"]
)
@login_required
def add_subject():
    """Create a new subject."""

    form = SubjectForm()

    if form.validate_on_submit():

        subject_code = (
            form.subject_code.data
            .strip()
            .upper()
        )

        subject_name = (
            form.subject_name.data
            .strip()
        )

        existing_subject = db.session.execute(
            db.select(Subject).where(
                Subject.subject_code == subject_code
            )
        ).scalar_one_or_none()

        if existing_subject:

            flash(
                "A subject with this code already exists.",
                "danger"
            )

            return render_template(
                "subjects/add.html",
                form=form
            )

        subject = Subject(
            subject_code=subject_code,
            subject_name=subject_name
        )

        db.session.add(subject)
        db.session.commit()

        flash(
            f"Subject '{subject_name}' added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "subjects.list_subjects"
            )
        )

    return render_template(
        "subjects/add.html",
        form=form
    )


@subjects_bp.route(
    "/<int:subject_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_subject(subject_id):
    """Edit an existing subject."""

    subject = db.get_or_404(
        Subject,
        subject_id
    )

    form = SubjectForm(obj=subject)

    if form.validate_on_submit():

        subject_code = (
            form.subject_code.data
            .strip()
            .upper()
        )

        subject_name = (
            form.subject_name.data
            .strip()
        )

        existing_subject = db.session.execute(
            db.select(Subject).where(
                Subject.subject_code == subject_code,
                Subject.id != subject.id
            )
        ).scalar_one_or_none()

        if existing_subject:

            flash(
                "Another subject already uses this code.",
                "danger"
            )

            return render_template(
                "subjects/edit.html",
                form=form,
                subject=subject
            )

        subject.subject_code = subject_code
        subject.subject_name = subject_name

        db.session.commit()

        flash(
            f"Subject '{subject_name}' updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "subjects.list_subjects"
            )
        )

    return render_template(
        "subjects/edit.html",
        form=form,
        subject=subject
    )


@subjects_bp.route(
    "/<int:subject_id>/delete",
    methods=["POST"]
)
@login_required
def delete_subject(subject_id):
    """Delete a subject."""

    subject = db.get_or_404(
        Subject,
        subject_id
    )

    form = DeleteSubjectForm()

    if not form.validate_on_submit():

        flash(
            "Invalid delete request.",
            "danger"
        )

        return redirect(
            url_for(
                "subjects.list_subjects"
            )
        )

    subject_name = subject.subject_name

    db.session.delete(subject)
    db.session.commit()

    flash(
        f"Subject '{subject_name}' deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "subjects.list_subjects"
        )
    )
