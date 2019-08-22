import os
import base64

from .core import define_root
from .utils import makedirs


@define_root(stage='init')
def init_instance_path(app):
    app.instance_path = os.path.join(app.root_path, 'var')


@define_root(stage='init', after=['instance_path'])
def init_secret_key(app):

    if app.secret_key:
        return

    secret_key_path = os.path.join(app.instance_path, 'etc', 'secret_key')
    if not os.path.exists(secret_key_path):
        makedirs(os.path.join(app.instance_path, 'etc'))
        with open(secret_key_path, 'wb') as fh:
            fh.write(base64.b16encode(os.urandom(32)))

    with open(secret_key_path, 'rb') as fh:
        app.secret_key = fh.read()
