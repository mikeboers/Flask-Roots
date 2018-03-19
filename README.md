Flask-Roots
===========

Flask Roots weaves together the various extensions that are the core of your app:

```
app = flask_roots.build_app(__name__, includes=['etc_config', 'log_files'])
```

Roots looks for the requested features in ``flask_roots`` entrypoints, linearizes
their self-described depedencies, and runs them.

Roots also comes with a few common extensions for the authors projects.


Warning to self
---------------

Flask roots used to manage the environment of the projects, including wrappers
for `bower`, `gem`, and `npm` so they would be a part of the virtualenv. It no
longer does this.

Flask roots also used to default to a fixed number of extensions. It no longer
does. For the behaviour when this change was made, build your app like:

```
app = flask_roots.build_app(__name__, include='''

    instance_path
    secret_key
    environ_config
    etc_config

    blank_static
    multi_static

    log_format
    log_files
    log_mail

    signed_session
    
    login
    acl
    mako
    images
    sqlalchemy
    mail

    route_re
    route_name

    error_templates

''')
globals().update(app.roots)

```


**WARNING: Everything below this line is before the major refactor.**

---

What Flask-Roots (Will) Provide
-------------------------------

In no particular order:

- a virtualenv with Ruby, Node, and Bower package freezing;
- a Flask app with extensions including:
    - Flask-Mako
    - Flask-SQLALchemy
    - Flask-WTForms
    - Flask-WTCrud (in development)
    - Flask-Images (currently Flask-ImgSizer)
    - Flask-Login
    - Flask-ACL
- basic logging
- basic error handling
- extensible configuration mechanism;
- HAML templates (triggered via a `.haml` extension);
- slightly more secure sessions;
- a `re` route converter;
- several Markdown extensions;
- CSS processing via SASS;
- Javascript concatenation and minification via Sprockets;
- basic schema migrations partialy by SQLAlchemy-Migrate.


Bootstrapping
-------------

For now, Roots assumes that you want to operate the web app out of the directory that it is in. It will set the `app.instance_path` to `os.path.join(app.root_path, 'var')`.

All of the run-time information should be stored in `app.instance_path`, so you can destroy that to start with a clean slate.

You must inform Roots of where to find the Flask app to serve. Create a `roots.py` module, and import your Flask app as `app` within it.


Configuration
-------------

The Flask config is build by executing a series of config files.

Roots will look for Python files in `{app.root_path}/etc/flask`, `{app.instance_path}/etc/flask`, and `<Flask-Roots>/etc/flask`. It will execute them ordered by their name. I tend to prefix these files with a three-digit sequence number to achieve a good order.

These files will be executed in the same namespace, which will always have `ROOT_PATH`, `INSTANCE_PATH`, and `setdefault` (which operates on the execution namespace).


Usage
-----

Once bootstrapped and configured, you can ask Roots to build your app:

~~~
from flask.ext.roots import make_app

app = make_app(__name__)

# Extract: db, mako, auth, login_manager, etc..
globals().update(app.roots.extensions)
~~~
