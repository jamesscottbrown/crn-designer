from vse.project.models import Project
from vse.project.forms import ProjectForm

from vse.data.forms import DataForm
from vse.data.models import Data

from vse.utils import flash_errors

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

import StringIO
import csv
import json

blueprint = Blueprint('project', __name__, url_prefix='/projects', static_folder='../static')


@blueprint.route('/')
@login_required
def list_projects():
    """List all user's projects."""
    return render_template('projects/list_projects.html')


@blueprint.route('/<int:project_id>')
def project(project_id):
    """List details of a project."""
    current_project = Project.query.filter_by(id=project_id).first()

    dataset_names = map(lambda x: x.name, current_project.data)

    if not current_project.public and current_project.user != current_user:
        flash('Not your project!', 'danger')
        return redirect('.')

    return render_template('projects/project.html', project=current_project, dataset_names=dataset_names)


@blueprint.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Edit details of a project."""
    current_project = Project.query.filter_by(id=project_id).first()

    if current_project.user != current_user:
        flash('Not your project!', 'danger')
        return redirect('.')

    form = ProjectForm(request.form)
    if form.validate_on_submit():
        form.populate_obj(current_project)
        current_project.save()
        flash('Project updated.', 'success')
        return redirect('projects/' + str(project_id))
    else:
        flash_errors(form)
    return render_template('projects/edit_project.html', form=form, current_project=current_project)


@blueprint.route('/<int:project_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_project(project_id):
    """Delete a project."""
    current_project = Project.query.filter_by(id=project_id).first()

    if current_project.user != current_user:
        flash('Not your project!', 'danger')
        return redirect('.')

    if request.method == "POST":
        current_project.delete()
        return redirect(url_for('project.list_projects'))

    return render_template('projects/delete_project.html', current_project=current_project)


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def new_project():
    """Add new project."""
    form = ProjectForm(request.form)
    if form.validate_on_submit():
        Project.create(name=form.name.data, description=form.description.data, variables=form.variables.data,
                       user_id=current_user.id, public=form.public.data)
        flash('New project created.', 'success')
        return redirect(url_for('project.list_projects'))
    else:
        flash_errors(form)
    return render_template('projects/new_project.html', form=form)



@blueprint.route('/<int:project_id>/data/add', methods=['GET', 'POST'])
@login_required
def add_dataset(project_id):
    """Add data to a project."""
    current_project = Project.query.filter_by(id=project_id).first()

    if current_project.user != current_user:
        flash('Not your project!', 'danger')
        return redirect('.')

    form = DataForm(request.form)
    if form.validate_on_submit():

        variable_names = Project.get_variables(project_id)

        csv_data = request.files[form.data.name].read()
        f = StringIO.StringIO(csv_data)
        reader = csv.reader(f, delimiter=',')

        data = []
        for row in reader:
            time = row.pop(0)
            for pair in zip(variable_names, row):
                data.append({"time": time, "variable": pair[0], "value": pair[1]})

        #print csv_data
        # open(os.path.join(UPLOAD_PATH, form.data.data), 'w').write(csv_data)

        Data.create(name=form.name.data, description=form.description.data, project_id=project_id,
                    data=json.dumps(data))

        flash('Data added to project.', 'success')
        return redirect(url_for('project.project', project_id=project_id))
    else:
        flash_errors(form)
    return render_template('data/new_data.html', form=form)



@blueprint.route('/<int:project_id>/data', methods=['GET', 'POST'])
def get_dataset(project_id):
    """View data from a project."""
    current_project = Project.query.filter_by(id=project_id).first()

    if not current_project.public and current_project.user != current_user:
        flash('Not your project!', 'danger')
        return redirect('.')

    data_sets = []
    for dataset in current_project.data:
        data_set = json.loads(dataset.data)
        for datum in data_set:
            datum["dataset"] = dataset.name

        data_sets.append({"name": dataset.name, "value": data_set})

    return json.dumps(data_sets)
