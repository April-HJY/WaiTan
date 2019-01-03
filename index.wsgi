import sae
from mysite import wsgi
import pylibmc
import sys
sys.modules['memcache'] = pylibmc

application = sae.create_wsgi_app(wsgi.application)
