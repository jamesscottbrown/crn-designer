from crn_designer.project.models import Project
from crn_designer.project.forms import ProjectForm

from crn_designer.utils import flash_errors

from crn_designer.project.solver_wrapper import getProblem

from flask import Blueprint, flash, redirect, render_template, request, url_for, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from CRNSynthesis.solverCaller import SolverCallerISAT, SolverCallerDReal
from numpy import savetxt

import StringIO
import csv
import json
import os

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

    if not current_project.spec:
        current_project.spec = 'false'  # lowercase as interpreted by JS

    return render_template('projects/project.html', project=current_project,
                           solvers_enabled=current_app.config.get("SOLVERS_ENABLED"))


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


@blueprint.route('/<int:project_id>/solve', methods=['GET', 'POST'])
@login_required
def solve_project(project_id):
    """Solve problem."""
    current_project = Project.query.filter_by(id=project_id).first()

    if current_project.user != current_user:
        flash('Not your project!', 'danger')
        return redirect('.')

    # save form details
    current_project.crn_semantics = request.form.get("semantics")
    current_project.solver = request.form.get("solver")
    current_project.save()

    # Construct CRN object
    print current_project.crn_sketch

    # Make directory for project
    directory = os.path.join(current_app.config.get("UPLOAD_FOLDER"), str(project_id))
    if not os.path.exists(directory):
        os.makedirs(directory)

    # construct CRN object and input files for solvers

    isat_problem, dreal_problem, flow, crn = getProblem(current_project.crn_sketch, current_project.spec)
    with open(os.path.join(directory, 'iSAT.hys'), 'w') as fp:
        fp.write(isat_problem)
    with open(os.path.join(directory, 'dReach.drh'), 'w') as fp:
        fp.write(dreal_problem)

    if request.form.get("solver") == "None":
        current_project.status = "Config file generated"
        current_project.save()
        return redirect(url_for('project.project', project_id=project_id))

    if not current_app.config.get("SOLVERS_ENABLED"):
        flash('SAT-ODE Solvers not enabled!', 'danger')
        return redirect(url_for('project.project', project_id=project_id))


    # Run solvers if requested
    current_project.status = "Running"
    current_project.save()

    if request.form.get("solver") == "iSAT":
        sc = SolverCallerISAT("./iSAT.hys", isat_path=current_app.config.get("ISAT_PATH"))
    elif request.form.get("solver") == "dReach":
        sc = SolverCallerDReal("./dReach.drh", dreal_path=current_app.config.get("DREAL_PATH"))

    result_files = sc.single_synthesis(cost=0)
    for file_name in result_files:
        vals, all_vals = sc.getCRNValues(file_name)

        initial_conditions, parametrised_flow = sc.get_full_solution(crn, flow, all_vals)

        with open(file_name+"-parameters.txt", "w") as f:
            f.write("Initial Conditions: %s\n" % initial_conditions)
            f.write("Flow: %\n" % parametrised_flow)

        t, sol, variable_names = sc.simulate_solutions(initial_conditions, parametrised_flow,
                                                       plot_name=file_name + "-simulation.png")
        savetxt(file_name + "-simulation.csv", sol, delimiter=",")

    current_project.status = "Complete"
    current_project.save()

    return redirect(url_for('project.project', project_id=project_id))


@blueprint.route('/<int:project_id>/data', methods=['GET'])
def download_data(project_id):

    current_project = Project.query.filter_by(id=project_id).first()

    if current_project.user != current_user and not current_project.public:
        flash('Not your project!', 'danger')
        return redirect(url_for('project.project', project_id=project_id))

    directory = os.path.join(current_app.config.get("UPLOAD_FOLDER"), str(project_id))
    file_path = os.path.join(directory, 'data.csv')

    if not os.path.isfile(file_path):
        return ""

    with open(file_path, 'r') as myfile:
        csv_data = myfile.read()
        f = StringIO.StringIO(csv_data)
        reader = csv.reader(f, delimiter=',')

    data = []
    variable_names = []
    for row in reader:
        if not variable_names:
            variable_names = row[1:]
            continue

        time = row.pop(0)
        for pair in zip(variable_names, row):
            data.append({"time": time, "variable": pair[0], "value": pair[1]})

    return json.dumps([data])


@blueprint.route('/<int:project_id>/iSAT', methods=['GET'])
def download_iSAT_file(project_id):

    current_project = Project.query.filter_by(id=project_id).first()

    if current_project.user != current_user and not current_project.public:
        flash('Not your project!', 'danger')
        return redirect(url_for('project.project', project_id=project_id))

    directory = os.path.join(current_app.config.get("UPLOAD_FOLDER"), str(project_id))
    file_path = os.path.join(directory, 'iSAT.hys')

    if not os.path.isfile(file_path):
        flash('iSAT file does not exist!', 'danger')
        return redirect(url_for('project.project', project_id=project_id))

    attachment_filename = current_project.name + ".hys"
    return send_from_directory(directory, 'iSAT.hys', as_attachment=True, attachment_filename=attachment_filename)

@blueprint.route('/<int:project_id>/dReach', methods=['GET'])
def download_dReach_file(project_id):

    current_project = Project.query.filter_by(id=project_id).first()

    if current_project.user != current_user and not current_project.public:
        flash('Not your project!', 'danger')
        return redirect(url_for('project.project', project_id=project_id))

    directory = os.path.join(current_app.config.get("UPLOAD_FOLDER"), str(project_id))
    file_path = os.path.join(directory, 'dReach.drh')

    if not os.path.isfile(file_path):
        flash('iSAT file does not exist!', 'danger')
        return redirect(url_for('project.project', project_id=project_id))

    attachment_filename = current_project.name + ".drh"
    return send_from_directory(directory, 'dReach.drh', as_attachment=True, attachment_filename=attachment_filename)


# attachment_filename

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

@blueprint.route('/<int:project_id>/copy', methods=['GET', 'POST'])
@login_required
def copy_project(project_id):
    """Copy a project."""
    current_project = Project.query.filter_by(id=project_id).first()

    if current_project.user != current_user and not current_project.public:
        flash('Not your project!', 'danger')
        return redirect(url_for('project.project', project_id=project_id))

    new_project = Project.create(name=current_project.name, description=current_project.description, crn_sketch=current_project.crn_sketch,
                       user_id=current_user.id, public=current_project.public)

    flash('New project created.', 'success')
    return redirect(url_for('project.project', project_id=new_project.id))



@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def new_project():
    """Add new project."""
    form = ProjectForm(request.form)
    if form.validate_on_submit():
        p = Project.create(name=form.name.data, description=form.description.data, crn_sketch='{}',
                           user_id=current_user.id, public=form.public.data)
        flash('New project created.', 'success')
        return redirect(url_for('project.project', project_id=p.id))
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

    if current_project.status:
        return "Cannot save, since project status is " + current_project.status

    print "\n\n\nRequest:"
    print request.form

    current_project.crn_sketch = unquote_plus(request.get_data()).decode('utf-8')

    # save state
    #current_project.solver = request.form["solver"]
    #current_project.semantics = request.form["semantics"]
    #current_project.actually_solve = request.form["actually-solve"]
    current_project.save()

    return "SUCCESS"

# TODO: merge save functions
@blueprint.route('/<int:project_id>/save', methods=['POST'])
@login_required
def save_spec(project_id):
    """Update saved spec for a project."""
    current_project = Project.query.filter_by(id=project_id).first()

    if current_project.user != current_user:
        flash('Not your project!', 'danger')
        return redirect('.')

    if current_project.status:
        return "Cannot save, since project status is " + current_project.status

    print "\n\n\nRequest:"
    print request.form

    current_project.spec = unquote_plus(request.get_data()).decode('utf-8')
    current_project.save()

    return "SUCCESS"

