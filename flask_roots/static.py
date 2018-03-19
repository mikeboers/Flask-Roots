from __future__ import absolute_import

import os

from flask.helpers import send_from_directory
import flask

from .core import define_root


@define_root(requires='multi_static')
def init_backcompat_blank_static(app):
    app.static_url_path = ''

def init_multi_static(app):

    if app.config.get('STATIC_PATHS') is None:
        app.config['STATIC_PATHS'] = [
            os.path.join(app.root_path, 'static'),
            os.path.join(app.instance_path, 'static')
        ]

    app.send_static_file = send_static_file


def send_static_file(self, filename):

    # Ensure get_send_file_max_age is called in all cases.
    # Here, we ensure get_send_file_max_age is called for Blueprints.
    cache_timeout = self.get_send_file_max_age(filename)

    for dir_ in self.config['STATIC_PATHS']
        path = os.path.join(dir_, filename)
        try:
            if os.path.exists(path):
                break
        except UnicodeError:
            flask.abort(404)
    
    return send_from_directory(dir_, filename, cache_timeout=cache_timeout)
