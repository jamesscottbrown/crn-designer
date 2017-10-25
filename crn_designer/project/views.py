from crn_designer.project.models import Project
from crn_designer.project.forms import ProjectForm

from crn_designer.utils import flash_errors

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

import StringIO
import csv
import json

from urllib import unquote_plus

blueprint = Blueprint('project', __name__, url_prefix='/projects', static_folder='../static')


@blueprint.route('/')
@login_required
def list_projects():
    """List all user's projects."""
    return render_template('projects/list_projects.html')




@blueprint.route('/<int:project_id>')
def project_no_backslash(project_id):
    return redirect(url_for('project.project', project_id=project_id))


@blueprint.route('/<int:project_id>/')
def project(project_id):
    """List details of a project."""
    current_project = Project.query.filter_by(id=project_id).first()

    if not current_project.public and current_project.user != current_user:
        flash('Not your project!', 'danger')
        return redirect('.')

    return render_template('projects/project.html', project=current_project)


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
        Project.create(name=form.name.data, description=form.description.data, crn_sketch='{}',
                       user_id=current_user.id, public=form.public.data)
        flash('New project created.', 'success')
        return redirect(url_for('project.list_projects'))
    else:
        flash_errors(form)
    return render_template('projects/new_project.html', form=form)

@blueprint.route('/<int:project_id>/saveCRN', methods=['POST'])
@login_required
def save_crn(project_id):
    """Update CRN for a project."""
    current_project = Project.query.filter_by(id=project_id).first()

    if current_project.user != current_user:
        flash('Not your project!', 'danger')
        return redirect('.')

    current_project.crn_sketch = unquote_plus(request.get_data()).decode('utf-8')
    current_project.save()
    return "SUCCESS"
