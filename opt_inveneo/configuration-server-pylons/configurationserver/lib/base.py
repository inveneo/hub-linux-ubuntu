"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from pylons import c, cache, config, g, request, response, session
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect_to
from pylons.decorators import jsonify, validate
from pylons.i18n import _, ungettext, N_
from pylons.templating import render

import configurationserver.lib.helpers as h
import configurationserver.model as model

# App Global Constants
DEFAULT_DYN_ATTRS={
    'INV_CONFIG_HOST': 'set me',
    'INV_CONFIG_HOST_TYPE': 'set me',
    'INV_HOSTNAME': 'set me',
    }
DEFAULT_DB_ATTRS={
    'INV_TIME_ZONE': "America/Los_Angeles",
    'INV_NTP_ON': True,
    'INV_NTP_SERVERS': "hub.local:pool.ntp.org",
    'INV_PROXY_ON': False,
    'INV_HTTP_PROXY': "hub.local",
    'INV_HTTP_PROXY_PORT': 8080,
    'INV_HTTPS_PROXY': "",
    'INV_HTTPS_PROXY_PORT': 8080,
    'INV_FTP_PROXY': "hub.local",
    'INV_FTP_PROXY_PORT': 8080,
    'INV_PHONE_HOME_ON': True,
    'INV_PHONE_HOME_REG': "http://community.inveneo.org/phonehome/reg",
    'INV_PHONE_HOME_CHECKIN': "http://community.inveneo.org/phonehome/checkin",
    'INV_LOCALE': "en_US.UTF-8",
    'INV_SINGLE_USER_LOGIN': True
    }
NONE = 'None'
NOT_FOUND = 'not found'
NONE_TYPE = "<type 'NoneType'>"
BUFF_SIZE=1024
MAC_REGEXP = '^[0-9a-f]{12,12}$'
LOCALE_REGEXP = '^[a-z][a-z](_[A-Z][A-Z](.[uU][tT][fF]-8)?)?$'
DEADDEADBEEF = 'deaddeadbeef'

class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            model.Session.remove()

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
