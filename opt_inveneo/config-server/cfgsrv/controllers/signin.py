from crypt import crypt
import logging

from cfgsrv.lib.base import *

log = logging.getLogger(__name__)

class SigninController(BaseController):

    def signin(self):
        log.debug('signin()')
        return render('/signin.mako')

    def signin_process(self):
        log.debug('signin_process()')
        username = request.params.get('username', '')
        password = request.params.get('password', '')
        admins = model.Session.query(model.Admin)
        admin = admins.filter(model.Admin.login_name == username).first()
        if admin:
            if crypt(password, admin.salt) == admin.password:
                session['admin'] = '%s %s' % (admin.first_name, admin.last_name)
                session.save()
                return redirect_to('/admin/dashboard')
        session['admin'] = None
        c.Error = {'signin': 'Username and password combination are not valid'}
        return render('/signin.mako')

    def signout(self):
        log.debug('signout()')
        session['admin'] = None
        session.save()
        return render('/signin.mako')
