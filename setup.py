from setuptools import setup


extras = {
    'mako': '''
        Flask-Mako
        Markdown
        PyHAML
    ''',
    'sqlalchemy': '''
        Flask-SQLAlchemy
    ''',
    'mail': '''
        Flask-Mail
    ''',
    'auth': '''
        Flask-Login
        Flask-ACL
    ''',
    'serve': '''
        gunicorn
        gevent
    ''',
    'images': '''
        Flask-Images
    ''',
    'manage': '''
        Baker
        jsmin
        watchdog
    ''',
}
extras['all'] = '\n'.join(extras.values())


setup(
    name='Flask-Roots',
    version='0.0.1',
    description="Mike's common Flask tools.",
    url='http://github.com/mikeboers/Flask-Roots',
    
    packages=['flask_roots'],
    
    author='Mike Boers',
    author_email='flask-roots@mikeboers.com',
    license='BSD-3',
    
    entry_points={

        'flask.commands': '''

            migrate = flask_roots.cli.migrate:main

        ''',
        
        'flask_roots': '''

            instance_path = flask_roots.app:init_instance_path
            secret_key = flask_roots.app:init_secret_key
            
            environ_config = flask_roots.config:init_environ_config
            etc_config = flask_roots.config:init_etc_config

            blank_static = flask_roots.static:init_blank_static
            multi_static = flask_roots.static:init_multi_static

            log_request_counter = flask_roots.logs:init_log_request_counter
            log_format = flask_roots.logs:init_log_format
            http_access_log = flask_roots.logs:init_http_access_log
            log_stderr = flask_roots.logs:init_log_stderr
            log_files = flask_roots.logs:init_log_files
            log_mail = flask_roots.logs:init_log_mail

            signed_session = flask_roots.session:init_signed_session
            
            login = flask_roots.vendor:init_flask_login
            acl = flask_roots.vendor:init_flask_acl
            mako = flask_roots.mako:init_mako
            images = flask_roots.vendor:init_flask_images
            sqlalchemy = flask_roots.vendor:init_flask_sqlalchemy
            mail = flask_roots.vendor:init_flask_mail

            route_re = flask_roots.routing:init_route_re
            route_name = flask_roots.routing:init_route_name

            error_templates = flask_roots.errors:init_error_templates

        '''
    },

    install_requires='''
        Flask    
    ''',
    extras_require=extras,

    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
    ],
    
)
