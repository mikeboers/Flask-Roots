


def init_flask_login(app):
    from flask_login import LoginManager
    login_mananger = LoginManager(app)
    app.roots['login_mananger'] = login_mananger # Old name.
    app.roots['authn'] = login_mananger # New name.
    login.user_callback = lambda uid: None # TODO: Why?


def init_flask_acl(app):
    from flask_acl import ACLManager
    authz = ACLManager(app)
    app.roots['auth'] = authz # Old name.
    app.roots['authz'] = authz # New name.


def init_flask_images(app):
    from flask_images import Images
    app.roots['images'] = Images(app)


def init_flask_sqlalchemy(app):
    from flask_sqlalchemy import sqlalchemy
    app.roots['db'] = db = SQLAlchemy(app)
    db.metadata.bind = db.engine # TODO: Why?


def init_flask_mail(app):
    from flask_mail import Mail
    app.roots['main'] = Mail(app)

