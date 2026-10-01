import base64
import binascii

import cv2
import numpy as np

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
from app.forms.student import DeleteStudentForm, StudentForm
from app.models import FaceEncoding, Student
from app.services.face_recognition import face_service


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


@students_bp.route(
    "/<int:student_id>/register-face",
    methods=["GET", "POST"]
)
@login_required
def register_face(student_id):
    """Register or replace a student's face encoding."""

    student = db.get_or_404(
        Student,
        student_id
    )

    if request.method == "GET":
        return render_template(
            "students/register_face.html",
            student=student
        )

    image_data = request.form.get(
        "image",
        ""
    )

    if not image_data:
        return {
            "success": False,
            "message": "No image was received."
        }, 400

    try:
        if "," in image_data:
            image_data = image_data.split(
                ",",
                1
            )[1]

        image_bytes = base64.b64decode(
            image_data,
            validate=True
        )

    except (
        ValueError,
        TypeError,
        binascii.Error
    ):
        return {
            "success": False,
            "message": "Invalid image data."
        }, 400

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        return {
            "success": False,
            "message": "The captured image could not be read."
        }, 400

    try:
        faces = face_service.detect_faces(
            image
        )

    except Exception as error:
        return {
            "success": False,
            "message": f"Face detection failed: {error}"
        }, 500

    if len(faces) == 0:
        return {
            "success": False,
            "message": (
                "No face detected. "
                "Make sure your face is clearly visible "
                "and try again."
            )
        }, 400

    if len(faces) > 1:
        return {
            "success": False,
            "message": (
                "Multiple faces detected. "
                "Only the student registering their face "
                "should be visible."
            )
        }, 400

    face = faces[0]

    try:
        encoding = face_service.generate_embedding(
            image,
            face
        )

    except Exception as error:
        return {
            "success": False,
            "message": f"Could not generate face encoding: {error}"
        }, 500

    existing_encoding = db.session.execute(
        db.select(FaceEncoding).where(
            FaceEncoding.student_id == student.id
        )
    ).scalar_one_or_none()

    if existing_encoding:
        existing_encoding.encoding = encoding
    else:
        new_encoding = FaceEncoding(
            student_id=student.id,
            encoding=encoding
        )

        db.session.add(
            new_encoding
        )

    db.session.commit()

    return {
        "success": True,
        "message": (
            f"Face registered successfully for {student.name}."
        )
    }


@students_bp.route(
    "/<int:student_id>/verify-face",
    methods=["GET", "POST"]
)
@login_required
def verify_face(student_id):
    """Verify a live face against the student's stored face."""

    student = db.get_or_404(
        Student,
        student_id
    )

    stored_encoding = db.session.execute(
        db.select(FaceEncoding).where(
            FaceEncoding.student_id == student.id
        )
    ).scalar_one_or_none()

    if stored_encoding is None:
        if request.method == "GET":
            flash(
                "This student does not have a registered face yet.",
                "warning"
            )

            return redirect(
                url_for(
                    "students.student_detail",
                    student_id=student.id
                )
            )

        return {
            "success": False,
            "message": "This student does not have a registered face."
        }, 400

    if request.method == "GET":
        return render_template(
            "students/verify_face.html",
            student=student
        )

    image_data = request.form.get(
        "image",
        ""
    )

    if not image_data:
        return {
            "success": False,
            "message": "No image was received."
        }, 400

    try:
        if "," in image_data:
            image_data = image_data.split(
                ",",
                1
            )[1]

        image_bytes = base64.b64decode(
            image_data,
            validate=True
        )

    except (
        ValueError,
        TypeError,
        binascii.Error
    ):
        return {
            "success": False,
            "message": "Invalid image data."
        }, 400

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        return {
            "success": False,
            "message": "The captured image could not be read."
        }, 400

    try:
        faces = face_service.detect_faces(
            image
        )

    except Exception as error:
        return {
            "success": False,
            "message": f"Face detection failed: {error}"
        }, 500

    if len(faces) == 0:
        return {
            "success": False,
            "message": (
                "No face detected. "
                "Please position your face clearly "
                "in front of the camera."
            )
        }, 400

    if len(faces) > 1:
        return {
            "success": False,
            "message": (
                "Multiple faces detected. "
                "Only one person should be visible."
            )
        }, 400

    try:
        new_embedding = face_service.generate_embedding(
            image,
            faces[0]
        )

        similarity = face_service.compare_embeddings(
            stored_encoding.encoding,
            new_embedding
        )

    except Exception as error:
        return {
            "success": False,
            "message": f"Face comparison failed: {error}"
        }, 500

    # SFace cosine similarity threshold.
    # We use this only for the verification test.
    threshold = 0.363

    matched = similarity >= threshold

    if matched:
        message = (
            f"Face matched successfully with {student.name}."
        )
    else:
        message = (
            "The captured face does not match the "
            "registered face."
        )

    return {
        "success": True,
        "matched": matched,
        "student_name": student.name,
        "roll_number": student.roll_number,
        "similarity": round(
            similarity,
            4
        ),
        "threshold": threshold,
        "message": message
    }
