import datetime
import os
import shutil
import urllib

import click
import flask
import sqlalchemy as sa


@click.command
@click.option('--dry-run', '-n', flag_value=True, default=False)
@click.option('--verbose', '-v', flag_value=True, default=False)
@click.option('--echo', '-e', flag_value=True, default=False)
@click.option('--no-backup', '-B', flag_value=True, default=False)
@flask.cli.with_appcontext
def main(dry_run, verbose, echo, no_backup):
    """Run Flask-Roots migrations"""
    
    sa_url = flask.current_app.config['SQLALCHEMY_DATABASE_URI']

    if not no_backup:
        split = urllib.parse.urlsplit(sa_url)
        if split.scheme == 'sqlite':
            dbpath = split.path
            if dbpath.startswith('/'):
                dbpath = dbpath[1:]
            backups = os.path.join(os.path.dirname(dbpath), 'backups')
            if not os.path.exists(backups):
                os.makedirs(backups)
            backup = os.path.join(
                backups,
                os.path.basename(dbpath) + '.' + datetime.datetime.utcnow().replace(microsecond=0).isoformat('T')
            )
            if verbose:
                print(f"Backing up SQLite:\n\tcp {dbpath}\n\tto {backup}")
            if not dry_run:
                shutil.copy(dbpath, backup)


    # Setup out migration tracking table.
    engine = sa.create_engine(sa_url, echo=echo)
    meta = sa.MetaData()
    table = sa.Table('schema_patches', meta,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('time', sa.DateTime, default=datetime.datetime.utcnow),
        sa.Column('name', sa.String),
    )
    table.create(checkfirst=True, bind=engine)

    root_path = flask.current_app.root_path
    print(f"Root path: {root_path}")

    with engine.connect() as con:
        applied = dict(list(con.execute(sa.select(table.c.name, table.c.time))))

    patchdir = os.path.join(root_path, 'etc', 'schema')
    for dirpath, dirnames, filenames in os.walk(patchdir, followlinks=True):

        # Need to sort this since Heroku lists them out of order.
        for filename in sorted(filenames):

            if not filename.endswith('.py'):
                continue

            fullname = os.path.join(dirpath, filename)
            relname = os.path.relpath(fullname, patchdir)
            basename, ext = os.path.splitext(relname)

            patches = []
            namespace = dict(patch=patches.append)
            code = compile(open(fullname).read(), fullname, 'exec')
            exec(code, namespace)

            # Old school.
            upgrade = namespace.get('upgrade')
            if upgrade and upgrade not in patches:
                patches.append(upgrade)
            

            for patch in patches:
                name = patch.__name__
                patch_name = relname + ':' + name
                
                try:
                    apply_time = applied.pop(patch_name)

                except KeyError:

                    if dry_run:
                        print(patch_name)
                        print('\twould apply')
                    else:
                        print(patch_name)
                        print('\tapplying...',)

                        patch(engine)

                        engine.execute(table.insert(), name=patch_name)
                        print('Done.')

                else:
                    if verbose:
                        print(patch_name)
                        print('\tapplied', apply_time.isoformat(' '))
    
    print(f"{len(applied)} orphan patches")
    for name, time in sorted(applied.items(), key=lambda x: (x[1], x[0])):
        print(f"\t{time} {name}")
                