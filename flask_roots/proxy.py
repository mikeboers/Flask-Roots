from werkzeug.middleware.proxy_fix import ProxyFix

from .core import define_root


@define_root
def init_proxy_fix(app):

    kw = {}
    for key in ('for', 'proto', 'host', 'port', 'prefix'):
        val = app.config.get(f'FIX_FORWARDED_{key.upper()}')
        if val is not None:
            kw[f'x_{key}'] = val
    
    if kw:
        app.wsgi_app = ProxyFix(app.wsgi_app, **kw)


