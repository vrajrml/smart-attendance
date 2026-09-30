from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class StudentForm(FlaskForm):

    roll_number = StringField(
        "Roll Number",
        validators=[
            DataRequired(),
            Length(max=30)
        ]
    )

    name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            Optional(),
            Email(),
            Length(max=150)
        ]
    )

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(max=20)
        ]
    )

    department = StringField(
        "Department",
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    semester = SelectField(
        "Semester",
        choices=[
            ("", "Select Semester"),
            ("1", "Semester 1"),
            ("2", "Semester 2"),
            ("3", "Semester 3"),
            ("4", "Semester 4"),
            ("5", "Semester 5"),
            ("6", "Semester 6"),
            ("7", "Semester 7"),
            ("8", "Semester 8"),
        ],
        validators=[
            Optional()
        ]
    )

    submit = SubmitField("Save Student")


class DeleteStudentForm(FlaskForm):
    submit = SubmitField("Delete Student")
