import copy
import os


def init_environ_config(app):
    # Pull from environment.
    for k, v in os.environ.items():
        if k.isupper() and k.startswith('FLASK_'):
            app.config[k[6:]] = v


def init_etc_config(app):

    root_path = app.root_path
    instance_path = app.instance_path

    # Scan $root/etc/flask for config files. They are included
    # in sorted order, without respect for the base of their path.
    config_files = set()
    for root in (app.root_path, app.instance_path):
        dir_path = os.path.join(root, 'etc', 'flask')
        if not os.path.exists(dir_path):
            continue
        for file_name in os.listdir(dir_path):
            if os.path.splitext(file_name)[1] == '.py':
                config_files.add(os.path.join(dir_path, file_name))
    config_files = sorted(config_files, key=lambda path: os.path.basename(path))

    config = app.config.copy()

    # These are here for convenience, but we don't want them to end up in
    # the actual config.
    helpers = {'setdefault': config.setdefault}
    for name, default in (
        ('ROOT_PATH', app.root_path),
        ('INSTANCE_PATH', app.instance_path),
    ):
        helpers[name] = config.get(name, default)

    for path in config_files:
        config.update(helpers)
        exec(open(path).read(), config)

    for k, v in config.items():
        if not k.isupper():
            continue
        if k in helpers:
            continue
        app.config[k] = v

