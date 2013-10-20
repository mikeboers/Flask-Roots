from __future__ import absolute_import

import os

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.imgsizer import ImgSizer
# from flask.ext.mail import Mail
from flask.ext.login import LoginManager
from flask.ext.acl import AuthManager


class Roots(object):

    def __init__(self, app):
        self.init_app(app)

    def init_app(self, app):

        # Establish two-way links.
        self.app = app
        app.roots = self
        app.extensions['roots'] = self

        from .config import setup_config
        setup_config(app)

        from .logs import setup_logs
        setup_logs(app)

        from .session import setup_session
        setup_session(app)

        self.login_manager = LoginManager(app)
        self.auth = AuthManager(app)

        from .mako import MakoTemplates
        self.mako = MakoTemplates(app)

        self.imgsizer = ImgSizer(app)

        self.db = SQLAlchemy(app)
        self.db.metadata.bind = self.db.engine # WTF do I need to do this for?!

        from .routing import setup_routing
        setup_routing(app)

        from .errors import setup_errors
        setup_errors(app)

