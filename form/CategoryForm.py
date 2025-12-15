from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.fields.simple import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message='Please enter the category name !'),Length(1,25),])
    desc = TextAreaField('Description', validators=[Length(0,500),])
    status = SelectField('Status', choices=[
        ('true', 'Active'),
        ('false', 'Inactive'),
    ])
    submit = SubmitField('Submit')