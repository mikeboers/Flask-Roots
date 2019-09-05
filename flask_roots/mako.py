from __future__ import absolute_import

import datetime
import json
import hashlib
import os
import re


from flask import g, current_app
from flask_mako import MakoTemplates as Base, render_template, render_template_string, render_template_def

import mako.template
import haml
from markupsafe import Markup

from .markdown import markdown
from .utils import makedirs


def init_mako(app):
    module_dir = app.config.setdefault('MAKO_MODULE_DIRECTORY', os.path.join(app.instance_path, 'tmp', 'mako'))
    mako = MakoTemplates(app)
    if module_dir:
        makedirs(module_dir)
    app.roots['mako'] = mako


def unicode_safe(x):
    return x if isinstance(x, Markup) else str(x)


# Monkey patch for error catching!
def def_template_uri(self):
    return self.parent.uri + '#' + self.callable_.__name__
mako.template.DefTemplate.uri = property(def_template_uri)


class MakoTemplates(Base):

    def __init__(self, *args, **kwargs):
        super(MakoTemplates, self).__init__(*args, **kwargs)

    def init_app(self, app):
        app.config.setdefault('MAKO_IMPORTS', []).append(
            'from %s import unicode_safe' % __name__
        )
        super(MakoTemplates, self).init_app(app)
        app.context_processor(self.process_context)
        # Force it to create the lookup now.
        app._mako_lookup = self.create_lookup(app)

    @staticmethod
    def create_lookup(app):

        if hasattr(Base, 'create_lookup'):
            # Flask-Mako==0.2
            lookup = Base.create_lookup(app)
        else:
            # Flask-Mako>=0.3
            from flask_mako import _create_lookup
            lookup = _create_lookup(app)

        lookup.default_filters = ['unicode_safe']
        
        get_template = lookup.get_template
        def new_get_template(name):
            g._mako_template_name = name
            return get_template(name)
        lookup.get_template = new_get_template
        
        lookup.template_args['preprocessor'] = preprocessor

        return lookup

    def process_context(self):
        return dict(
            fuzzy_time=fuzzy_time,
            markdown=markdown,
            json=json.dumps,
            static=static,
            auth=current_app.extensions.get('acl'),
        )


_static_etags = {}

def static(file_name):

    file_name = file_name.strip('/')

    # Serve out of 'static' and 'var/static'.
    for dir_name in 'static', 'var/static':
        file_path = os.path.join(current_app.root_path, dir_name, file_name)
        if os.path.exists(file_path):
            mtime = os.path.getmtime(file_path)
            if file_path not in _static_etags or _static_etags[file_path][0] != mtime:
                hash_ = hashlib.sha1(open(file_path, 'rb').read()).hexdigest()[:8]
                _static_etags[file_path] = (mtime, hash_)
            return '/%s?e=%s' % (file_name, _static_etags[file_path][1])

    return '/' + file_name


def fuzzy_time(d, now=None):
    
    if isinstance(d, (int, float)):
        d = datetime.datetime.fromtimestamp(int(d))

    now = now or datetime.datetime.utcnow()
    diff = now - d
    s = diff.seconds + diff.days * 24 * 3600
    future = s < 0
    days, s = divmod(abs(s), 60 * 60 * 24)
    prefix = 'in ' if future else ''
    postfix = '' if future else ' ago'
    if days > 30:
        return 'on ' + d.strftime('%B %d, %Y')
    elif days == 1:
        out = '1 day'
    elif days > 1:
        out = '{0} days'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        out = '{0} seconds'.format(s)
    elif s < 3600:
        out = '{0} minutes'.format(s/60)
    else:
        out = '{0} hours'.format(s/3600)
    return prefix + out + postfix


_inline_control_re = re.compile(r'%{([^}]+)}')
def _inline_callback(m):
    statement = m.group(1).strip()
    return '\\\n%% %s%s\n' % (statement, '' if statement.startswith('end') else ':')
def inline_control_statements(source):
    return _inline_control_re.sub(_inline_callback, source)


_post_white_re = re.compile(r'([$%]){(.*?)-}\s*')
_pre_white_re = re.compile(r'\s*([$%]){-(.*?)}')
def whitespace_control(source):
    source = _post_white_re.sub(r'\1{\2}', source)
    return _pre_white_re.sub(r'\1{\2}', source)


_tiny_mako_re = re.compile(r'([$%]{.*?}|<%1? .*?%>)')
def tiny_mako(source):
    parts = _tiny_mako_re.split(source)
    for i in range(0, len(parts), 2):
        parts[i] = parts[i] and ('<%%text>%s</%%text>' % parts[i])
    return ''.join(parts)


def preprocessor(source):
    if getattr(g, '_mako_template_name', '').endswith('.haml'):
        source = haml.preprocessor(source)
    return inline_control_statements(whitespace_control(source))
