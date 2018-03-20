
import flask_roots

app = flask_roots.build_app(__name__, include='''

    instance_path
    secret_key
    environ_config
    etc_config

    blank_static
    multi_static


    log_format
    log_stderr
    log_files
    #log_mail
    http_access_log

    signed_session
    
    login
    acl
    mako
    images
    #sqlalchemy
    mail

    route_re
    route_name

    error_templates

''', config=dict(
    DEBUG=True,
))

globals().update(app.roots)


@app.route('/')
def index():
    return 'HELLO'


app.run()