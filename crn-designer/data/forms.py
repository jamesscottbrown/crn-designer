from flask_wtf import Form
from wtforms import StringField, FileField
from wtforms.validators import DataRequired, EqualTo, Length

from .models import Data


class DataForm(Form):
    """Form to add data to project."""

    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=25)])
    description = StringField('Description', validators=[Length(max=40)])
    data = FileField('Data')

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(DataForm, self).__init__(*args, **kwargs)

    def validate(self):
        """Validate the form."""
        initial_validation = super(DataForm, self).validate()
        if not initial_validation:
            return False

        return True
