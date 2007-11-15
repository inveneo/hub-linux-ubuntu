import crypt
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
            if self._user_credetintials_ok(user):
                return redirect_to('/admin/dashboard')
        return redirect_to('/signin/signin')

    def signout(self):
        session['user'] = None
        session.save()
        return render('/signin/signin.mako')
    
    def _user_credetintials_ok(self, user):
        if user:
            log.debug('authenticating :' + user.login_name)                
            pw = self._get_encrypted_password(request.params['password'], user.salt)
            if user.password == pw:
                session['user'] = user.first_name
                session.save()
                return True
        return False

    def _get_encrypted_password(self, password, salt):
        pw = crypt.crypt(password, salt)
        return pw    

    def _get_user(self, name):
        name = str(name)
        try:
            u_q = model.Session.query(model.User).filter(model.User.login_name == name).one()
            return u_q
        except:
            return None




