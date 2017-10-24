from flask_wtf import Form
from wtforms import StringField, SelectField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Length

from .models import Specification


class SpecificationForm(Form):
    """Form to create new specification."""

    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=25)])
    description = StringField('Description', validators=[Length(max=40)])
    specification = StringField('Specification', validators=[])
    variable = SelectField('Variable')
    project_id = HiddenField()

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(SpecificationForm, self).__init__(*args, **kwargs)

    def validate(self):
        """Validate the form."""
        initial_validation = super(SpecificationForm, self).validate()
        if not initial_validation:
            return False

        return True
