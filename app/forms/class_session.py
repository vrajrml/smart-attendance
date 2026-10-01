from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField, TimeField
from wtforms.validators import DataRequired


class ClassSessionForm(FlaskForm):
    """Form for creating and editing class sessions."""

    subject_id = SelectField(
        "Subject",
        coerce=int,
        validators=[
            DataRequired()
        ]
    )

    session_date = DateField(
        "Session Date",
        format="%Y-%m-%d",
        validators=[
            DataRequired()
        ]
    )

    start_time = TimeField(
        "Start Time",
        format="%H:%M",
        validators=[
            DataRequired()
        ]
    )

    end_time = TimeField(
        "End Time",
        format="%H:%M",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Save Session")


class DeleteClassSessionForm(FlaskForm):
    """Form for deleting a class session."""

    submit = SubmitField("Delete Session")
