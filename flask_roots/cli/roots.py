import pkg_resources

import click


@click.command
# @flask.cli.with_appcontext
def main():
    """Print Flask-Roots' registered "roots"."""
    for ep in pkg_resources.iter_entry_points('flask_roots'):

        print(ep)
        func = ep.load()

        root = getattr(func, '__flask_roots_config__', {})
        for k, v in root.items():
            print(f'\t{k}: {v!r}')
        
        print()
