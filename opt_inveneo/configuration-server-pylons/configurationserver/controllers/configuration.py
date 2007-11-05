import logging
import paste
import socket

from configurationserver.lib.base import *

log = logging.getLogger(__name__)
NONE = 'None'
NOT_FOUND = 'not found'
NONE_TYPE = "<type 'NoneType'>"
DEFAULT_ATTRS={
    'INV_CONFIG_HOST': socket.gethostname(),
    'INV_CONFIG_HOST_TYPE': 'hub',
    'INV_HOSTNAME': 'station-',
    'INV_MAC': "DEFAULT_MAC",
    'INV_TIME_ZONE': "America/Los_Angeles",
    'INV_NTP_ON': True,
    'INV_NTP_SERVERS': "hub.local:pool.ntp.org",
    'INV_PROXY_ON': False,
    'INV_HTTP_PROXY': "hub.local",
    'INV_HTTP_PROXY_PORT': 8080,
    'INV_HTTPS_PROXY': "",
    'INV_HTTPS_PROXY_PORT': 8080,
    'INV_FTP_PROXY': "hub.local",
    'INV_FTP_PROXY_PORT': 8080,
    'INV_PHONE_HOME_ON': True,
    'INV_PHONE_HOME_REG': "http://community.inveneo.org/phonehome/reg",
    'INV_PHONE_HOME_CHECKIN': "http://community.inveneo.org/phonehome/checkin",
    'INV_LOCALE': "en_US.UTF-8",
    'INV_SINGLE_USER_LOGIN': True
    }

class ConfigurationController(BaseController):

    ###########################
    # instance  helper methods
    ###########################    
    def get_tmp_config_file_path(self, id, category):
        log.debug('get tmp config file for id: ' + id + ' and category ' + category )

        local_station_file = 'saved-configuration/' + category + '/' + id + '.tar.gz'

        if not h.does_file_exist(local_station_file, log):
            log.warning('config file not found')
            return NOT_FOUND
        else:
            log.info('config file found')
            return h.copy_to_temp_file(local_station_file, log)
       
    def return_config_file(self, name, category):
        name = str(name)
        category = str(category)

        log.debug('return config file for name: ' + name + ' and category ' + category )

        if name == NONE:
            log.error('Need a valid user name')
            return

        tmp_config_file = self.get_tmp_config_file_path(name, category)

        if tmp_config_file == NOT_FOUND:
            log.error('No config file found')
            return

        fapp = paste.fileapp.FileApp(tmp_config_file)
        return fapp(request.environ, self.start_response)

    def create_config_map(self, q):
        return {
            'INV_CONFIG_HOST': socket.gethostname(),
            'INV_CONFIG_HOST_TYPE': 'hub',
            'INV_HOSTNAME': 'station-' + str(q.mac),
            'INV_TIME_ZONE': str(q.timezone),
            'INV_NTP_ON': str(q.ntp_on),
            'INV_NTP_SERVERS': str(q.ntp_servers),
            'INV_PROXY_ON': str(q.proxy_on),
            'INV_HTTP_PROXY': str(q.http_proxy),
            'INV_HTTP_PROXY_PORT': str(q.http_proxy_port),
            'INV_HTTPS_PROXY': str(q.https_proxy),
            'INV_HTTPS_PROXY_PORT': str(q.https_proxy_port),
            'INV_FTP_PROXY': str(q.ftp_proxy),
            'INV_FTP_PROXY_PORT': str(q.ftp_proxy_port),
            'INV_PHONE_HOME_ON': str(q.phone_home_on),
            'INV_PHONE_HOME_REG': str(q.phone_home_reg),
            'INV_PHONE_HOME_CHECKIN': str(q.phone_home_checkin),
            'INV_LOCALE': str(q.locale),
            'INV_SINGLE_USER_LOGIN': str(q.single_user_login)
            }

    def return_initial_config_file(self, name, config_map):
        name = str(name)

        log.debug('return initial config file for name: ' + name)

        tmp_file_path = h.tmp_file_name(log)
        output = open(tmp_file_path, 'a+')
        properties = []

        properties.append('#Initial Configuration\n')

        for key, value in config_map.iteritems():
            properties.append(str(key) + '=' + str(value) + '\n')
 
        output.writelines(properties)
        output.close()

        fapp = paste.fileapp.FileApp(tmp_file_path)
        return fapp(request.environ, self.start_response)

 
    ###########################
    # controller methods
    ###########################    
    def index(self):
        return

    def get_user_config(self, id):
        log.debug('get user config for: ' + str(id))
        return self.return_config_file(id, 'user')

    def get_station_config(self, id):
        log.debug('get station config for: ' + str(id))
        return self.return_config_file(id, 'station')

    def get_station_initial_config(self, id):
        mac_address = str(id)

        log.debug('get station initial config for mac: ' + mac_address)

        if mac_address == NONE:
            log.error('Need a valid station MAC address')
            return

        initialconfig_q = model.sac.query(model.Config).get_by(mac = mac_address)

        log.info('type : ' + str(type(initialconfig_q)))

        if str(type(initialconfig_q)) == NONE_TYPE: # this code stinks
            return self.return_initial_config_file(mac_address, 
                                                   DEFAULT_ATTRS)
        else:
            return self.return_initial_config_file(mac_address, 
                                                   self.create_config_map(initialconfig_q))

    def save_user_config(self):
        log.debug('save user config')

        if not h.does_parameter_exist(request, 'config_file', log):
            log.error('No config file found')
            return

        config_file = request.params['config_file']

        return 'save user config' + config_file

    def save_station_config(self):
        log.debug('save station config')
        return 'save station config'

    def save_station_initial_config(self):
        log.debug('save station initial config')
        return 'save station initial config'


    
