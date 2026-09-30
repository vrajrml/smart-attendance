from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from app.forms.student import DeleteStudentForm, StudentForm
from app.models import Student


students_bp = Blueprint(
    "students",
    __name__,
    url_prefix="/students"
)


@students_bp.route("/")
@login_required
def list_students():
    """Display students and support searching."""

    search = request.args.get("search", "").strip()

    query = db.select(Student)

    if search:
        search_pattern = f"%{search}%"

        query = query.where(
            db.or_(
                Student.roll_number.ilike(search_pattern),
                Student.name.ilike(search_pattern),
                Student.email.ilike(search_pattern)
            )
        )

    query = query.order_by(Student.name)

    students = db.session.execute(
        query
    ).scalars().all()

    delete_form = DeleteStudentForm()

    return render_template(
        "students/list.html",
        students=students,
        search=search,
        delete_form=delete_form
    )


@students_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_student():
    """Create a new student."""

    form = StudentForm()

    if form.validate_on_submit():

        roll_number = form.roll_number.data.strip()

        existing_student = db.session.execute(
            db.select(Student).where(
                Student.roll_number == roll_number
            )
        ).scalar_one_or_none()

        if existing_student:
            flash(
                "A student with this roll number already exists.",
                "danger"
            )

            return render_template(
                "students/add.html",
                form=form
            )

        email = form.email.data.strip() or None

        if email:

            existing_email = db.session.execute(
                db.select(Student).where(
                    Student.email == email
                )
            ).scalar_one_or_none()

            if existing_email:

                flash(
                    "A student with this email already exists.",
                    "danger"
                )

                return render_template(
                    "students/add.html",
                    form=form
                )

        student = Student(
            roll_number=roll_number,
            name=form.name.data.strip(),
            email=email,
            phone=form.phone.data.strip() or None,
            department=form.department.data.strip() or None,
            semester=int(form.semester.data)
            if form.semester.data
            else None
        )

        db.session.add(student)
        db.session.commit()

        flash(
            f"Student '{student.name}' added successfully.",
            "success"
        )

        return redirect(
            url_for("students.list_students")
        )

    return render_template(
        "students/add.html",
        form=form
    )


@students_bp.route("/<int:student_id>")
@login_required
def student_detail(student_id):
    """Display one student's details."""

    student = db.get_or_404(
        Student,
        student_id
    )

    return render_template(
        "students/detail.html",
        student=student
    )


@students_bp.route(
    "/<int:student_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_student(student_id):
    """Edit an existing student."""

    student = db.get_or_404(
        Student,
        student_id
    )

    form = StudentForm(obj=student)

    if form.validate_on_submit():

        roll_number = form.roll_number.data.strip()

        existing_student = db.session.execute(
            db.select(Student).where(
                Student.roll_number == roll_number,
                Student.id != student.id
            )
        ).scalar_one_or_none()

        if existing_student:

            flash(
                "Another student already uses this roll number.",
                "danger"
            )

            return render_template(
                "students/edit.html",
                form=form,
                student=student
            )

        email = form.email.data.strip() or None

        if email:

            existing_email = db.session.execute(
                db.select(Student).where(
                    Student.email == email,
                    Student.id != student.id
                )
            ).scalar_one_or_none()

            if existing_email:

                flash(
                    "Another student already uses this email.",
                    "danger"
                )

                return render_template(
                    "students/edit.html",
                    form=form,
                    student=student
                )

        student.roll_number = roll_number
        student.name = form.name.data.strip()
        student.email = email
        student.phone = form.phone.data.strip() or None
        student.department = (
            form.department.data.strip() or None
        )

        student.semester = (
            int(form.semester.data)
            if form.semester.data
            else None
        )

        db.session.commit()

        flash(
            f"Student '{student.name}' updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "students.student_detail",
                student_id=student.id
            )
        )

    return render_template(
        "students/edit.html",
        form=form,
        student=student
    )


@students_bp.route(
    "/<int:student_id>/delete",
    methods=["POST"]
)
@login_required
def delete_student(student_id):
    """Delete a student."""

    student = db.get_or_404(
        Student,
        student_id
    )

    form = DeleteStudentForm()

    if not form.validate_on_submit():
        flash(
            "Invalid delete request.",
            "danger"
        )

        return redirect(
            url_for("students.list_students")
        )

    student_name = student.name

    db.session.delete(student)
    db.session.commit()

    flash(
        f"Student '{student_name}' deleted successfully.",
        "success"
    )

    return redirect(
        url_for("students.list_students")
    )
