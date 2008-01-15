import crypt
import logging

from cfgsrv.lib.base import *

log = logging.getLogger(__name__)

class SigninController(BaseController):

    def signin(self):
        return render('/signin/signin.mako')

    def signin_process(self):
        log.debug('signin process')
        if len(request.params) > 1:
            admin = self._get_admin(request.params['username'])
            if self._admin_credetintials_ok(admin):
                return redirect_to('/admin/dashboard')
        error = {}
        error['signin'] = 'Username and password combination are not valid.'
        c.Error = error
        return render('/signin/signin.mako')

    def signout(self):
        session['admin'] = None
        session.save()
        return render('/signin/signin.mako')
    
    def _admin_credetintials_ok(self, admin):
        if admin:
            log.debug('authenticating: ' + admin.login_name)                
            pw = self._get_encrypted_password(request.params['password'], \
                    admin.salt)
            if admin.password == pw:
                session['admin'] = admin.first_name
                session.save()
                return True
        return False

    def _get_encrypted_password(self, password, salt):
        pw = crypt.crypt(password, salt)
        return pw    

    def _get_admin(self, name):
        name = str(name)
        try:
            u_query = model.Session.query(model.Admin)
            u_q = u_query.filter(model.Admin.login_name == name).one()
            return u_q
        except:
            return None
