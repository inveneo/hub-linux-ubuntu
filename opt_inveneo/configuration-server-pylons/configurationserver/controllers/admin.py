import logging
import cgi

from configurationserver.lib.base import *

log = logging.getLogger(__name__)
NONE = 'None'
NONE_TYPE = "<type 'NoneType'>"

class AdminController(BaseController):

    ###########################
    # instance  helper methods
    ###########################    
    def get_config_entry_by_id_or_mac_or_create(self, key):
        key = str(key)

        log.debug('Key: ' + key)

        if key == NONE: 
            q = model.Config()            
        else:
            log.info("len of key " + str(len(key)))
            if len(key) == 12:
                log.info('using mac')
                q = model.sac.query(model.Config).get_by(mac = key)
            else:
                q = model.sac.query(model.Config).get(key)

        if str(type(q)) == NONE_TYPE: # this code stinks
            q = model.Config()

        return q
       

    ###########################
    # controller methods
    ###########################    

    def index(self):
        return redirect_to('/admin/dashboard')

    def dashboard(self):
        return render('/admin/dashboard.mako')

    def edit(self, id):
        c.Config = self.get_config_entry_by_id_or_mac_or_create(id)
        return render('/admin/config_edit.mako')

    def config_add(self):
        c.Config = model.Config()
        return render('/admin/config_edit.mako')

    def config_edit_process(self, id):

        newconfig_q = self.get_config_entry_by_id_or_mac_or_create(id)

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
