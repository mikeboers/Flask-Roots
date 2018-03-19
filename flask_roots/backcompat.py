import os


def init_instance_path(app):
    app.instance_path = os.path.join(app.root_path, 'var')

