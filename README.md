# CRN Designer

This is a web-app that allows a user to draw a parametrized sketch of a chemical reaction network, and a functional specification, and synthesises a set of parameters and initial conditions that satisfy this specification, using the method described in [Syntax-Guided Optimal Synthesis for Chemical Reaction Networks](https://link.springer.com/chapter/10.1007/978-3-319-63390-9_20).

The JavaScript components implementing the [CRN sketch editor](https://github.com/jamesscottbrown/crn-sketch-editor) and [specification editor](https://github.com/jamesscottbrown/TimeRails) are stored from separate repositories, and included as [git submodules](https://git-scm.com/book/en/Git-Tools-Submodules).



## Quickstart

### With Docker

If you have Docker installed, you can run in development mode by simply running:

    docker-compose -f docker-compose.yml up

and then opening [``http://127.0.0.1:5000``](http://127.0.0.1:5000)
    
The first time this command is run, it will take a while to build a container image; on subsequent occasions the already-built image is used, and it starts running much faster.

### Without Docker

First, set your app's secret key as an environment variable. For example,
add the following to ``.bashrc`` or ``.bash_profile``:

    export crn_designer_SECRET='something-really-secret'


Before running shell commands, set the ``FLASK_APP`` and ``FLASK_DEBUG``
environment variables:

    export FLASK_APP=/path/to/autoapp.py
    export FLASK_DEBUG=1

Then run the following commands to bootstrap your environment:

    git clone https://github.com/jamesscottbrown/crn-designer
    cd crn_designer
    git submodule init
    git submodule upgrade
    pip install -r requirements/dev.txt

Once you have installed your DBMS, run the following to create your app's
database tables and perform the initial migration:

    flask db init
    flask db migrate
    flask db upgrade
    
 You can now run the application:
    
    flask run


## Migrations

Whenever a database migration needs to be made. Run the following commands ::

    flask db migrate

This will generate a new migration script. Then run ::

    flask db upgrade

To apply the migration.

For a full migration command reference, run ``flask db --help``.
