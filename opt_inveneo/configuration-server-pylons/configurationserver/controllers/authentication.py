import logging

from configurationserver.lib.base import *

log = logging.getLogger(__name__)

class AuthenticationController(BaseController):

    def __before__(self, action, **params):
        log.debug("before user login check: " + str(session.get('admin')))

        if session.get('admin') == None:
            return redirect_to('/signin/signin')

