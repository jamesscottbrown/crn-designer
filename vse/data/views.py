from vse.data.models import Data
from vse.data.forms import DataForm

from vse.utils import flash_errors

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

blueprint = Blueprint('data', __name__, url_prefix='/data', static_folder='../static')


@blueprint.route('/<int:data_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_data(data_id):
    """Delete a data set."""
    data = Data.query.filter_by(id=data_id).first()
    current_project = data.project

    if current_project.user != current_user:
        flash('Not your project!', 'danger')
        return redirect('.')

    if request.method == "POST":
        data.delete()
        return redirect(url_for('project.project', project_id=current_project.id))

    return render_template('data/delete_data.html', data=data, current_project=current_project)

