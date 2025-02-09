import os
import pathlib as pl
import subprocess

import click
import flask


@click.command
@click.option('--dry-run', '-n', flag_value=True, default=False)
@click.option('--watch', '-w', flag_value=True, default=False)
@flask.cli.with_appcontext
def main(dry_run, watch):
    """Run Flask-Roots builders"""
        
    root = pl.Path(flask.current_app.root_path)
    
    code = 0
    css_src = root / 'css'
    if css_src.exists():
        css_dst = root / 'var' / 'static' / 'css'

        for src in css_src.iterdir():
            if src.name.startswith('.'):
                continue
            if src.is_dir():
                continue

            if src.suffix == '.less':
                dst = css_dst / (src.stem + '.css')
                cmd = ['lesscpy', '-x', str(src), str(dst)]
                print(' '.join(cmd))
                if not dry_run:
                    code = subprocess.call(cmd) or code

    if watch:
        print("---")
        print("Watching for changes; ctrl-C to abort.")
        os.execvp('watchmedo', ['watchmedo', 'shell-command',
            '-R', # Recursive.
            '-W', # Drop events while running.
            '-c', 'echo ---; echo "# $(date)"; flask build',
            '-p', '*.less',
            css_src
        ])
    
    exit(code)


