from __future__ import absolute_import

import os

from flask.helpers import send_from_directory
import flask

from .core import define_root


@define_root(requires=['multi_static'])
def init_blank_static(app):
    app.static_url_path = ''

def init_multi_static(app):

    if app.config.get('STATIC_PATHS') is None:
        app.config['STATIC_PATHS'] = [
            os.path.join(app.root_path, 'static'),
            os.path.join(app.instance_path, 'static')
        ]

    # Remove the existing one.
    app.view_functions.pop('static', None)

    # Use ours.
    # This is inspired by how the default one is registered.
    app.add_url_rule(
        app.static_url_path + "/<path:filename>",
        endpoint="static",
        host=None, # ??
        view_func=lambda filename: send_static_file(app, filename)
    )


def send_static_file(app, filename):

    # Ensure get_send_file_max_age is called in all cases.
    # Here, we ensure get_send_file_max_age is called for Blueprints.
    max_age = app.get_send_file_max_age(filename)

    for dir_ in app.config['STATIC_PATHS']:
        path = os.path.join(dir_, filename)
        try:
            if os.path.exists(path):
                break
        except UnicodeError:
            flask.abort(404)
    
    return send_from_directory(dir_, filename, max_age=max_age)
