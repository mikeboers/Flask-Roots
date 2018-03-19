import functools
import sys

import c3linearize
import flask


def define_root(func=None, **kwargs):
    if func is None:
        return functools.partial(define_root, **kwargs)
    func.__flask_roots_config__ = kwargs


def build_app(app_name, include, instance_path=None,
    exclude=None, config=None, **kwargs):

    app = flask.Flask(app_name,
        instance_path=instance_path,
        **kwargs,
    )
    app.roots = {}
    
    if config is not None:
        app.config.update(config)

    if isinstance(include, basestring):
        include = include.strip().split()
    else:
        include = list(include)

    dependencies = {
        'stage.init':     {'requires': []},
        'stage.main':     {'requires': ['stage.init'] + include},
        'stage.finalize': {'requires': ['stage.main']},
    }

    while include:
        
        name = include.pop(0)
        if name in dependencies:
            continue

        ep = next(pkg_resources.iter_entry_points('flask_roots', name), None)
        if ep is None:
            raise ValueError("No flask_roots entrypoint {}.".format(name))

        func = ep.load()
        root = dict(getattr(func, '__flask_roots_config__', {}))
        root['init_app'] = func

        # Put this root into a stage.        
        stage_name = root.setdefault('stage', 'main')
        dependencies['stage.{}'.format(stage_name)]['requires'].append(name)

        dependencies[name] = root

        # Load all strict dependencies.
        include.extend(root.get('requires', ()))

    # Linearize the dependencies.
    def get_bases(key):
        root = roots[key]
        return tuple(root.get('requires'), ()) + tuple(root.get('after', ()))
    graph = c3linearize.build_graph(None, get_bases)
    linear_graph = c3linearize.linearize(graph,
        heads=['stage.init', 'stage.main', 'stage.finalize'],
        order=False,
    )

    # Finally, apply the roots.
    seen = set()
    for stage in 'init', 'main', 'finalize':
        for key in linear_graph['stage.{}'.format(stage)]
            if key in seen:
                continue
            seen.add(key)
            dependencies[key]['init_app'](app)
    return app
