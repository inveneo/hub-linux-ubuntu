import logging
import cgi
import os
import shutil

from cfgsrv.lib.base import *
from cfgsrv.controllers.authentication import *

log = logging.getLogger(__name__)

def Get_initial_config(config = model.Config()):
    config.mac = str(g.DEFAULT_MAC)

    config.lang = g.DEFAULT_DB_ATTRS['INV_LANG']
    config.time_zone = g.DEFAULT_DB_ATTRS['INV_TIME_ZONE']

    config.config_host = g.DEFAULT_DB_ATTRS['INV_CONFIG_HOST']
    config.config_host_type = g.DEFAULT_DB_ATTRS['INV_CONFIG_HOST_TYPE']

    config.proxy_on = g.DEFAULT_DB_ATTRS['INV_PROXY_ON']

    config.ntp_on = g.DEFAULT_DB_ATTRS['INV_NTP_ON']
    config.ntp_servers = g.DEFAULT_DB_ATTRS['INV_NTP_SERVERS']

    config.hub_docs_dirs_on = g.DEFAULT_DB_ATTRS['INV_HUB_DOCS_DIRS_ON']
    config.local_shared_docs_dir_on = \
            g.DEFAULT_DB_ATTRS['INV_LOCAL_SHARED_DOCS_DIR_ON']
    config.local_user_docs_dir_on = \
            g.DEFAULT_DB_ATTRS['INV_LOCAL_USER_DOCS_DIR_ON']

    config.phone_home_on = g.DEFAULT_DB_ATTRS['INV_PHONE_HOME_ON']
    config.phone_home_reg_url = g.DEFAULT_DB_ATTRS['INV_PHONE_HOME_REG_URL']
    config.phone_home_checkin_url = \
            g.DEFAULT_DB_ATTRS['INV_PHONE_HOME_CHECKIN_URL']
    return config

class AdminController(AuthenticationController):

    ###########################
    # helper methods
    ###########################

    ###########################
    # instance  helper methods
    ###########################    
    def _get_config_entry_by_id_or_mac_or_create(self, key):
        key = str(key)

        log.debug('get config entry with key: ' + key)

        o_q = model.Session.query(model.Config)
        if len(key) == 12:
            try:
                q = o_q.filter(model.Config.mac == key).one()
                log.debug('found by mac')
            except:
                q = model.Config()
                q.mac = key
                log.debug('create new config')
        else:
            q = o_q.get(key)
            log.debug('found by primary key')
                
        if str(type(q)) == NONE_TYPE: # this code stinks
            q = model.Config()

        return q
       
    def _validate_configuration(self, config, is_edit):
        log.debug('config validation')
        error = {}

        if not is_edit:
            try:
                model.Session.query(model.Config).filter(model.Config.mac == config.mac).one()
                error['mac'] = 'MAC is already being used'
            except:
                pass

        if not h.validate_with_regexp(MAC_REGEXP, config.mac, True, log):
            error['mac'] = 'MAC address must be 12 hex lower case values, no separator' 
        if not h.validate_with_regexp(LOCALE_REGEXP, config.lang, True, log):
            error['lang'] = 'Must be a valid lang string. E.g. en_UK.utf-8'

        return error

    def _copy_reset_config(self, dir):
        for f in os.listdir(dir):
            if str(f).endswith('.tar.gz'):
                log.debug(dir + '../blank.tar.gz' + ' overwrites  ' + f)
                shutil.copyfile(dir + '../blank.tar.gz', dir + '/' + f)

    def _get_inveneo_server(self):
        return model.Session.query(model.Server).filter(model.Server.name == 'inveneo').one()

    ###########################
    # controller methods
    ###########################    
    def index(self):
        return redirect_to('/admin/dashboard')

    def dashboard(self):
        c.Server = self._get_inveneo_server()

        return render('/admin/dashboard.mako')

    def set_server_on(self, id):
        log.debug('switching server on or off (no "on" parameter is toggle')
        q = self._get_inveneo_server()

        if not h.does_parameter_exist(request, 'on'):
            log.debug('toggling')
            q.server_on = h.toggle_boolean(q.server_on)
        else:
            log.debug('setting on: ' + request.params['on'])
            q.server_on = request.params['on'] == 'True'

        model.Session.update(q)
        model.Session.commit()

        return redirect_to('/admin/dashboard')

    def reset_client_config(self, id):
        log.debug('reseting all configurations for clients and stations')
        q = self._get_config_entry_by_id_or_mac_or_create(id)
        q = Get_initial_config(q)

        model.Session.update(q)
        model.Session.commit()

        self._copy_reset_config(h.get_config_dir_station())
        self._copy_reset_config(h.get_config_dir_user())

        return redirect_to('/admin/dashboard')    

    def set_initial_config(self):
        q = self._get_config_entry_by_id_or_mac_or_create(g.DEFAULT_MAC)
        model.Session.save(q)
        model.Session.commit()

        c.Config = None

        return self.edit(g.DEFAULT_MAC)

    def edit(self, id):
        c.Config = self._get_config_entry_by_id_or_mac_or_create(id)
        c.Edit = True
        return render('/admin/config_edit.mako')

    def config_remove(self, id):
        mac = str(id)

        if mac == NONE:
            log.error('Need a valid unique mac identifier')
            return abort(400)

        try:
            q = model.Session.query(model.Config).filter(model.Config.mac == mac).one()
            model.Session.delete(q)
            model.Session.commit()
        except:
            return abort(400)

        return redirect_to('/admin/list_initial_configurations')

    def config_add(self):
        c.Config = model.Config()
        c.Edit = False
        return render('/admin/config_edit.mako')

    def config_edit_process(self, id):
        log.debug('config edit process for: ' + str(id))
        newconfig_q = self._get_config_entry_by_id_or_mac_or_create(id)
        is_edit = False

        try:
            newconfig_q.mac = cgi.escape(request.POST['mac'])
        except:
            is_edit = True
        newconfig_q.lang = cgi.escape(request.POST['lang']) 
        newconfig_q.time_zone = cgi.escape(request.POST['time_zone'])

        newconfig_q.config_host = cgi.escape(request.POST['config_host']) 
        newconfig_q.config_host_type = \
                cgi.escape(request.POST['config_host_type']) 

        newconfig_q.proxy_on = h.is_checkbox_set(request, 'proxy_on', log)
        newconfig_q.ntp_on = h.is_checkbox_set(request, 'ntp_on', log)
        newconfig_q.ntp_servers = cgi.escape(request.POST['ntp_servers']) 

        newconfig_q.hub_docs_dirs_on = \
                h.is_checkbox_set(request, 'hub_docs_dirs_on', log)
        newconfig_q.local_shared_docs_dir_on = \
                h.is_checkbox_set(request, 'local_shared_docs_dir_on', log)
        newconfig_q.local_user_docs_dir_on = \
                h.is_checkbox_set(request, 'local_user_docs_dir_on', log)

        newconfig_q.phone_home_on = \
                h.is_checkbox_set(request, 'phone_home_on', log)
        newconfig_q.phone_home_reg_url = \
                cgi.escape(request.POST['phone_home_reg_url']) 
        newconfig_q.phone_home_checkin_url = \
                cgi.escape(request.POST['phone_home_checkin_url']) 

        error = self._validate_configuration(newconfig_q, is_edit)

        if len(error) == 0:
            log.debug('found error in one of the values')
            model.Session.save(newconfig_q)
            model.Session.commit()
        else:
            c.Error = error
            c.Edit = is_edit
            c.Config = newconfig_q
            return render('/admin/config_edit.mako')

        c.Config = None

        return redirect_to('/admin/config_edit_done')

    def config_edit_done(self):
        return redirect_to('/admin/list_initial_configurations')
        
    def station_remove(self, id):
        mac = str(id)

        if mac == NONE:
            log.error('Need a valid unique mac identifier')
            return abort(400)

        try:
            q = model.Session.query(model.Station).filter(model.Station.mac == mac).one()
            model.Session.delete(q)
            model.Session.commit()
        except:
            return abort(400)

        return redirect_to('/admin/list_station_configurations')

    def list_initial_configurations(self):
        config_q = model.Session.query(model.Config)
        c.Configs = config_q.all()
        return render('/admin/list_initial_configurations.mako')

    def list_station_configurations(self):
        config_q = model.Session.query(model.Station)
        c.Stations = config_q.all()
        return render('/admin/list_station_configurations.mako')
