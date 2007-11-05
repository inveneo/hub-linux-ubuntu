import logging
import cgi

from configurationserver.lib.base import *

log = logging.getLogger(__name__)
NONE = 'None'

class AdminController(BaseController):

    ###########################
    # controller methods
    ###########################    

    def index(self):
        return redirect_to('/admin/list')

    def edit(self, id):
        c.Config = model.sac.query(model.Config).get(id)
        return render('/admin/config_edit.mako')

    def config_add(self):
        c.Config = model.Config()
        return render('/admin/config_edit.mako')

    def config_edit_process(self, id):
        if str(id) == NONE: 
            newconfig_q = model.Config()            
        else:
            newconfig_q = model.sac.query(model.Config).get(id)

        newconfig_q.mac = cgi.escape(request.POST['mac'])
        newconfig_q.timezone = cgi.escape(request.POST['timezone'])
        newconfig_q.ntp_on = h.is_checkbox_set(request, 'ntp_on', log)
        newconfig_q.ntp_servers = cgi.escape(request.POST['ntp_servers']) 
        newconfig_q.proxy_on = h.is_checkbox_set(request, 'proxy_on', log)
        newconfig_q.http_proxy = cgi.escape(request.POST['http_proxy']) 
        newconfig_q.http_proxy_port = cgi.escape(request.POST['http_proxy_port']) 
        newconfig_q.https_proxy = cgi.escape(request.POST['https_proxy']) 
        newconfig_q.https_proxy_port = cgi.escape(request.POST['https_proxy_port']) 
        newconfig_q.ftp_proxy = cgi.escape(request.POST['ftp_proxy']) 
        newconfig_q.ftp_proxy_port = cgi.escape(request.POST['ftp_proxy_port']) 
        newconfig_q.phone_home_on = h.is_checkbox_set(request, 'phone_home_on', log)
        newconfig_q.phone_home_reg = cgi.escape(request.POST['phone_home_reg']) 
        newconfig_q.phone_home_checkin = cgi.escape(request.POST['phone_home_checkin']) 
        newconfig_q.locale = cgi.escape(request.POST['locale']) 
        newconfig_q.single_user_login = h.is_checkbox_set(request, 'single_user_login', log)
        model.sac.session.flush()
        
        return redirect_to('/admin/config_edit_done')

    def config_edit_done(self):
        return redirect_to('/admin/list')
        
    def list(self):
        config_q = model.sac.query(model.Config)
        c.Configs = config_q.all()
        return render('/admin/list.mako')
