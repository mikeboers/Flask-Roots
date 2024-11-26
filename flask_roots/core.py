import functools
import os
import re

import pkg_resources

import flask


def define_root(func=None, **kwargs):
    if func is None:
        return functools.partial(define_root, **kwargs)
    func.__flask_roots_config__ = kwargs
    return func


def build_app(app_name, include, exclude=None, config=None, **kwargs):

    kwargs.setdefault('root_path', os.environ.get('FLASK_ROOT_PATH'))
    kwargs.setdefault('instance_path', os.environ.get('FLASK_INSTANCE_PATH'))

    app = flask.Flask(app_name,
        **kwargs
    )
    app.roots = {}
    
    if config is not None:
        app.config.update(config)

    if isinstance(include, str):
        include = re.sub(r'#.+?$', '\n', include, 0, re.MULTILINE | re.DOTALL)
        include = include.strip().split()
    else:
        include = list(include)


    roots = {
        'stage.init':     {'requires': []},
        'stage.main':     {'requires': ['stage.init']},
        'stage.finalize': {'requires': ['stage.main']},
    }

    while include:
        
        name = include.pop(0)
        if name in roots:
            continue

        ep = next(pkg_resources.iter_entry_points('flask_roots', name), None)
        if ep is None:
            raise ValueError("No flask_roots entrypoint {}.".format(name))

        func = ep.load()
        root = dict(getattr(func, '__flask_roots_config__', {}))
        root['init_app'] = func

        # Put this root into a stage.        
        stage_name = root.setdefault('stage', 'main')
        roots['stage.{}'.format(stage_name)]['requires'].append(name)

        roots[name] = root

        # Load all strict dependencies.
        for key in 'requires', 'after':
            value = root.get(key, ())
            if not isinstance(value, (list, tuple)):
                raise TypeError("Flask root {} {}} is non-string.".format(name, key), value)
        
        include.extend(root.get('requires', ()))

    seen = set()
    for stage in 'init', 'main', 'finalize':
        key = 'stage.' + stage
        stack = [key]
        todo = {key: list(roots[key]['requires'])}
        while stack:

            key = stack[-1]
            try:
                next_ = todo[key].pop(0)
            except IndexError:
                stack.pop(-1)
                root = roots.get(key, {})
                func = root.get('init_app')
                if func:
                    func(app)
                continue

            if next_ in seen:
                continue
            seen.add(next_)

            root = roots.get(name)
            if not root:
                continue

            stack.append(next_)
            requires = list(root.get('requires', ()))
            requires.extend(root.get('after', ()))
            todo[next_] = requires

    return app
