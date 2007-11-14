import logging

from configurationserver.lib.base import *

log = logging.getLogger(__name__)

class SigninController(BaseController):

    def signin(self):
        return render('/signin/signin.mako')

    def signin_process(self):
        log.debug('signin process')
        if len(request.params) > 1 and \
         request.params['password'] == request.params['username']:
            session['user'] = request.params['username']
            session.save()
            return redirect_to('/admin/dashboard')
        else:
            return redirect_to('/signin/signin')

    def signout(self):
        session['user'] = None
        session.save()
        return render('/signin/signin.mako')



