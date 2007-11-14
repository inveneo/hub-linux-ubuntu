import logging

from configurationserver.lib.base import *

log = logging.getLogger(__name__)

class AuthenticationController(BaseController):

    def __before__(self, action, **params):
        log.debug("before check " + str(session.get('user')))

        if session.get('user') == None:
            return redirect_to('/signin/signin')

