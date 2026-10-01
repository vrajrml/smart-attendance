import base64
import binascii
from datetime import date, datetime

import cv2
import numpy as np
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from app.models import Attendance, ClassSession, FaceEncoding, Student
from app.services.face_recognition import face_service


attendance_bp = Blueprint(
    "attendance",
    __name__,
    url_prefix="/attendance"
)


MATCHING_THRESHOLD = 0.363


@attendance_bp.route("/")
@login_required
def list_attendance_sessions():
    sessions = db.session.execute(
        db.select(ClassSession)
        .order_by(
            ClassSession.session_date.desc(),
            ClassSession.start_time.desc()
        )
    ).scalars().all()

    return render_template(
        "attendance/list.html",
        sessions=sessions
    )


@attendance_bp.route("/history")
@login_required
def attendance_history():

    from_date = request.args.get("from_date", "").strip()
    to_date = request.args.get("to_date", "").strip()
    student_id = request.args.get("student_id", "").strip()
    subject_id = request.args.get("subject_id", "").strip()
    status = request.args.get("status", "").strip()

    query = (
        db.select(Attendance)
        .join(Attendance.student)
        .join(Attendance.session)
        .join(ClassSession.subject)
        .order_by(
            ClassSession.session_date.desc(),
            ClassSession.start_time.desc(),
            Attendance.marked_at.desc()
        )
    )

    if from_date:
        try:
            from_date_value = date.fromisoformat(from_date)
            query = query.where(
                ClassSession.session_date >= from_date_value
            )
        except ValueError:
            from_date = ""

    if to_date:
        try:
            to_date_value = date.fromisoformat(to_date)
            query = query.where(
                ClassSession.session_date <= to_date_value
            )
        except ValueError:
            to_date = ""

    if student_id:
        try:
            query = query.where(
                Attendance.student_id == int(student_id)
            )
        except ValueError:
            student_id = ""

    if subject_id:
        try:
            query = query.where(
                ClassSession.subject_id == int(subject_id)
            )
        except ValueError:
            subject_id = ""

    if status in {"present", "late", "absent"}:
        query = query.where(
            Attendance.status == status
        )
    else:
        status = ""

    records = db.session.execute(query).scalars().all()

    students = db.session.execute(
        db.select(Student).order_by(Student.roll_number)
    ).scalars().all()

    from app.models import Subject

    subjects = db.session.execute(
        db.select(Subject).order_by(Subject.subject_code)
    ).scalars().all()

    return render_template(
        "attendance/history.html",
        records=records,
        students=students,
        subjects=subjects,
        from_date=from_date,
        to_date=to_date,
        student_id=student_id,
        subject_id=subject_id,
        status=status
    )


@attendance_bp.route(
    "/session/<int:session_id>",
    methods=["GET", "POST"]
)
@login_required
def attendance_scanner(session_id):

    session = db.get_or_404(
        ClassSession,
        session_id
    )

    # ---------------------------------------------------------
    # Session status protection
    # ---------------------------------------------------------

    if session.attendance_finalized:
        flash(
            "Attendance for this session has already been finalized and locked.",
            "warning"
        )
        return redirect(
            url_for("attendance.list_attendance_sessions")
        )

    if session.session_status == "upcoming":
        flash(
            "This class session has not started yet. "
            "Attendance scanning will become available when the session starts.",
            "info"
        )
        return redirect(
            url_for("attendance.list_attendance_sessions")
        )

    if session.session_status == "ended":
        flash(
            "This class session has ended. "
            "Face scanning is no longer available. "
            "Use Manage to review attendance.",
            "warning"
        )
        return redirect(
            url_for("attendance.manage_attendance", session_id=session.id)
        )

    # ---------------------------------------------------------
    # GET
    # ---------------------------------------------------------

    if request.method == "GET":
        return render_template(
            "attendance/scanner.html",
            session=session
        )

    # ---------------------------------------------------------
    # POST - Face Scanner
    # ---------------------------------------------------------

    image_data = request.form.get("image", "").strip()

    if not image_data:
        return {
            "success": False,
            "message": "No image was received."
        }, 400

    try:
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(
            image_data,
            validate=True
        )

    except (ValueError, binascii.Error):
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
            "message": "Unable to process the image."
        }, 400

    faces = face_service.detect_faces(image)

    if len(faces) == 0:
        return {
            "success": False,
            "message": "No face detected. Please position your face clearly in the camera."
        }, 400

    if len(faces) > 1:
        return {
            "success": False,
            "message": "Multiple faces detected. Please make sure only one person is in the camera."
        }, 400

    face = faces[0]

    try:
        new_embedding = face_service.generate_embedding(
            image,
            face
        )
    except Exception:
        return {
            "success": False,
            "message": "Unable to generate a face embedding."
        }, 400

    registered_faces = db.session.execute(
        db.select(FaceEncoding)
        .join(FaceEncoding.student)
    ).scalars().all()

    if not registered_faces:
        return {
            "success": False,
            "message": "No registered student faces are available."
        }, 400

    best_student = None
    best_score = -1.0

    for face_encoding in registered_faces:

        try:
            score = face_service.compare_embeddings(
                face_encoding.encoding,
                new_embedding
            )
        except Exception:
            continue

        if score > best_score:
            best_score = score
            best_student = face_encoding.student

    if best_student is None:
        return {
            "success": False,
            "message": "Face could not be matched with a registered student."
        }, 400

    if best_score < MATCHING_THRESHOLD:
        return {
            "success": False,
            "message": (
                "Face not recognized. "
                f"Match confidence: {best_score:.4f}"
            )
        }, 400

    existing_attendance = db.session.execute(
        db.select(Attendance).where(
            Attendance.student_id == best_student.id,
            Attendance.session_id == session.id
        )
    ).scalar_one_or_none()

    if existing_attendance:
        return {
            "success": False,
            "message": (
                f"{best_student.name} is already marked "
                f"{existing_attendance.status} for this session."
            )
        }, 400

    attendance = Attendance(
        student_id=best_student.id,
        session_id=session.id,
        status="present",
        confidence=round(best_score, 4)
    )

    db.session.add(attendance)
    db.session.commit()

    return {
        "success": True,
        "message": (
            f"Attendance marked successfully for "
            f"{best_student.name}."
        ),
        "student": {
            "id": best_student.id,
            "name": best_student.name,
            "roll_number": best_student.roll_number
        },
        "confidence": round(best_score, 4)
    }


@attendance_bp.route(
    "/session/<int:session_id>/manage",
    methods=["GET", "POST"]
)
@login_required
def manage_attendance(session_id):

    session = db.get_or_404(
        ClassSession,
        session_id
    )

    students = db.session.execute(
        db.select(Student).order_by(Student.roll_number)
    ).scalars().all()

    existing_records = db.session.execute(
        db.select(Attendance).where(
            Attendance.session_id == session.id
        )
    ).scalars().all()

    attendance_by_student = {
        record.student_id: record
        for record in existing_records
    }

    # ---------------------------------------------------------
    # POST protection
    # ---------------------------------------------------------

    if request.method == "POST":

        if session.attendance_finalized:
            flash(
                "Attendance for this session has already been finalized and locked.",
                "warning"
            )
            return redirect(
                url_for(
                    "attendance.manage_attendance",
                    session_id=session.id
                )
            )

        if session.session_status == "upcoming":
            flash(
                "This class session has not started yet. "
                "Attendance cannot be marked before the session starts.",
                "warning"
            )
            return redirect(
                url_for(
                    "attendance.manage_attendance",
                    session_id=session.id
                )
            )

        for student in students:

            status = request.form.get(
                f"status_{student.id}",
                "absent"
            )

            if status not in {
                "present",
                "late",
                "absent"
            }:
                status = "absent"

            record = attendance_by_student.get(student.id)

            if record:
                record.status = status
            else:
                record = Attendance(
                    student_id=student.id,
                    session_id=session.id,
                    status=status,
                    confidence=None
                )
                db.session.add(record)

        db.session.commit()

        flash(
            "Attendance updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "attendance.manage_attendance",
                session_id=session.id
            )
        )

    return render_template(
        "attendance/manage.html",
        session=session,
        students=students,
        attendance_by_student=attendance_by_student
    )


@attendance_bp.route(
    "/session/<int:session_id>/finalize",
    methods=["POST"]
)
@login_required
def finalize_attendance(session_id):

    session = db.get_or_404(
        ClassSession,
        session_id
    )

    if session.attendance_finalized:
        flash(
            "Attendance for this session is already finalized.",
            "info"
        )
        return redirect(
            url_for(
                "attendance.manage_attendance",
                session_id=session.id
            )
        )

    # Attendance should only be finalized after the class ends.
    if session.session_status != "ended":
        flash(
            "Attendance can only be finalized after the class session has ended.",
            "warning"
        )
        return redirect(
            url_for(
                "attendance.manage_attendance",
                session_id=session.id
            )
        )

    students = db.session.execute(
        db.select(Student).order_by(Student.roll_number)
    ).scalars().all()

    existing_records = db.session.execute(
        db.select(Attendance).where(
            Attendance.session_id == session.id
        )
    ).scalars().all()

    attendance_by_student = {
        record.student_id: record
        for record in existing_records
    }

    # Anyone without an attendance record is automatically absent.
    for student in students:

        if student.id not in attendance_by_student:

            db.session.add(
                Attendance(
                    student_id=student.id,
                    session_id=session.id,
                    status="absent",
                    confidence=None
                )
            )

    session.attendance_finalized = True
    session.finalized_at = datetime.utcnow()

    db.session.commit()

    flash(
        "Attendance finalized successfully. "
        "The session is now locked.",
        "success"
    )

    return redirect(
        url_for(
            "attendance.manage_attendance",
            session_id=session.id
        )
    )
