from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class SubjectForm(FlaskForm):
    """Form for creating and editing subjects."""

    subject_code = StringField(
        "Subject Code",
        validators=[
            DataRequired(),
            Length(max=30)
        ]
    )

    subject_name = StringField(
        "Subject Name",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    submit = SubmitField("Save Subject")


class DeleteSubjectForm(FlaskForm):
    """Form for deleting a subject."""

    submit = SubmitField("Delete Subject")
