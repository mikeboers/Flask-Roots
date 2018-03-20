from __future__ import absolute_import

from urllib import quote
import datetime
import itertools
import logging.handlers
import os
import socket
import sys
import time

from flask import request, g, Response

from .core import define_root



WHITE_PIXEL = 'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='.decode('base64')


@define_root(stage='init')
def init_log_request_counter(app):

    _request_counter = itertools.count(1)
    @app.before_request
    def prepare_for_injection():
        g.log_request_counter = next(_request_counter)
        g.log_start_time = time.time()


def init_uuid_pixel(app):
    @app.route('/_uuid.gif')
    def uuid_pixel():

        etags = request.if_none_match.as_set()
        etag = list(etags)[0] if etags else None

        uuid = request.cookies.get('uuid')

        res = Response(WHITE_PIXEL, mimetype='image/gif')

        if etag and (not uuid or etag != uuid):

            if uuid:
                http_access_logger.info('uuid migrated from %s to %s' % (etag, uuid))
                res.headers.add('Etag', uuid)
            else:
                http_access_logger.info('uuid restored to %s' % etag)
                res.set_cookie('uuid', etag, max_age=3600*24*365*20)

        if uuid and not etag:
            res.headers.add('Etag', uuid)

        if not request.cookies.get('uuid_validated'):
            res.set_cookie('uuid_validated', '1')

        res.expires = time.time() + 3600
        res.cache_control.private = True
        res.cache_control.must_revalidate = True
        res.cache_control.max_age = 0

        return res


@define_root(requires=['log_request_counter'])
def init_http_access_log(app):

    log_name = app.config.get('HTTP_ACCESS_LOG_NAME', 'http.access')
    log = logging.getLogger(log_name)

    @app.after_request
    def log_request(response):

        # Get (or create) a token for the user. I call it "uuid" because I don't
        # want to set a cookie called "tracker". But you are reading this comment,
        # so....
        uuid = request.cookies.get('uuid')
        if uuid is None:
            uuid = os.urandom(8).encode('hex')
            response.set_cookie('uuid', uuid, max_age=60*60*24*365*20)

        meta = {
            'uuid': uuid,
        }
        if request.referrer:
            meta['referrer'] = request.referrer # Does this need quoting?

        log.info('%(method)s %(path)s -> %(status)s in %(duration).1fms' % {
            'method': request.method,
            'path': quote(request.path.encode('utf8')),
            'status': response.status_code,
            'duration': 1000 * (time.time() - g.log_start_time),
        } + ('; ' if meta else '') + ' '.join('%s=%s' % x for x in sorted(meta.iteritems())))

        return response




class RequestContextInjector(logging.Filter):

    static = {'pid': os.getpid()}

    def filter(self, record):
        record.__dict__.update(self.static)
        try:
            record.remote_addr = request.remote_addr
            record.request_counter = getattr(g, 'log_request_counter')
        except (AttributeError, RuntimeError):
            record.remote_addr = None
            record.request_counter = 0
        return True


@define_root(requires=['log_request_counter'], stage='finalize')
def init_log_format(app):

    root = logging.getLogger()
    root.setLevel(logging.DEBUG if app.debug else logging.INFO)

    format_ = app.config.get('LOG_FORMAT', '%(asctime)s %(levelname)-8s pid:%(pid)d req:%(request_counter)d ip:%(remote_addr)s %(name)s - %(message)s')
    formatter = logging.Formatter(format_)

    injector = RequestContextInjector()

    # Add our injector and filter to everything that doesn't already have it.
    for handler in root.handlers:
        if True or handler.formatter is None:
            handler.setFormatter(formatter)
        handler.addFilter(injector)




class PatternedFileHandler(logging.FileHandler):
    def _open(self):
        file_path = self.baseFilename.format(
            datetime=datetime.datetime.utcnow().strftime('%Y-%m-%d.%H-%M-%S'),
            pid = os.getpid(),
        )
        return open(file_path, 'wb')


def init_log_stderr(app):
    logging.getLogger(None).addHandler(logging.StreamHandler())


def init_log_files(app):

    log_dir = app.config.get('LOG_FILE_DIRECTORY', os.path.join(app.instance_path, 'log', 'python'))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    name_pattern = app.config.get('LOG_FILE_PATTERN', '{datetime}.{pid}.log')
    logging.getLogger(None).addHandler(PatternedFileHandler(os.path.join(log_dir, name_pattern)))



def init_log_mail(app):

    if app.debug:
        return

    mail_handler = logging.handlers.SMTPHandler(
        '127.0.0.1',
        app.config.get('DEFAULT_MAIL_SENDER', 'flask_roots@{}'.format(socket.gethostname())),
        app.config.get('ADMINS', ['{}@{}'.format(os.getlogin(), socket.gethostname())]),
        'Website Error',
    )
    mail_handler.setLevel(logging.ERROR)
    logging.getLogger(None).addHandler(mail_handler)





