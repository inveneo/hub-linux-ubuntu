import logging

from configurationserver.lib.base import *

log = logging.getLogger(__name__)

class SigninController(BaseController):

    def signin(self):
        return render('/signin/signin.mako')

    def signin_process(self):
        log.debug('signin process')
        if len(request.params) > 1:
            user = self._get_user(request.params['username'])
            if user and user.password == request.params['password']:
                session['user'] = user.first_name
                session.save()
                return redirect_to('/admin/dashboard')
            else:
                return redirect_to('/signin/signin')

    def signout(self):
        session['user'] = None
        session.save()
        return render('/signin/signin.mako')

    def _get_user(self, name):
        name = str(name)
        try:
            u_q = model.Session.query(model.User).filter(model.User.login_name == name).one()
            return u_q
        except:
            return None




