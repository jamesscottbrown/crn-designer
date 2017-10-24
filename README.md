# CRN Designer

This is a web-app that allows a user to draw a parametrized sketch of a chemical reaction network, and a functional specification, and synthesises a set of parameters and initial conditions that satisfy this specification, using the method described in [Syntax-Guided Optimal Synthesis for Chemical Reaction Networks](https://link.springer.com/chapter/10.1007/978-3-319-63390-9_20).

The JavaScript components implementing the [CRN sketch editor](https://github.com/jamesscottbrown/crn-sketch-editor) and [specification editor](https://github.com/jamesscottbrown/TimeRails) are available form separate repositories.



## Quickstart

First, set your app's secret key as an environment variable. For example,
add the following to ``.bashrc`` or ``.bash_profile``.

    export VSE_SECRET='something-really-secret'


Before running shell commands, set the ``FLASK_APP`` and ``FLASK_DEBUG``
environment variables:

    export FLASK_APP=/path/to/autoapp.py
    export FLASK_DEBUG=1

Then run the following commands to bootstrap your environment:

    git clone https://github.com/jamesscottbrown/crn-designer
    cd crn-designer
    pip install -r requirements/dev.txt
    bower install
    flask run

You will see a pretty welcome screen.

Once you have installed your DBMS, run the following to create your app's
database tables and perform the initial migration ::

    flask db init
    flask db migrate
    flask db upgrade
    flask run


## Migrations

Whenever a database migration needs to be made. Run the following commands ::

    flask db migrate

This will generate a new migration script. Then run ::

    flask db upgrade

To apply the migration.

For a full migration command reference, run ``flask db --help``.
