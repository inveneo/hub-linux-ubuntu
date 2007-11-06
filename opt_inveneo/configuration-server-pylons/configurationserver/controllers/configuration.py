import logging
import paste
import socket

from configurationserver.lib.base import *

log = logging.getLogger(__name__)
NONE = 'None'
NOT_FOUND = 'not found'
NONE_TYPE = "<type 'NoneType'>"
DEFAULT_DYN_ATTRS={
    'INV_CONFIG_HOST': 'set me',
    'INV_CONFIG_HOST_TYPE': 'set me',
    'INV_HOSTNAME': 'set me',
    }
DEFAULT_DB_ATTRS={
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
BUFF_SIZE=1024

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

    def save_config_file(self, request, name, category):
        name = str(name)
        category = str(category)

        log.debug('return config file for name: ' + name + ' and category ' + category )
        
        if not h.does_parameter_exist(request, 'config_file', log):
            log.error('No config file found')
            return

        config_file = request.POST['config_file']
        tmp_dest_file = h.tmp_file_name(log)

        # curl --fail -s -w %{size_upload} -F config_file=@<file> \
        # http://localhost:5000/configuration/save_user_config/<name> -v

        if config_file.file:
            out = open(tmp_dest_file, "w+")
            while 1:
                byte = config_file.file.read(BUFF_SIZE)
                if not byte: break
                out.write(byte)
            out.close()

        h.copy_from_temp_file('saved-configuration/' + category + '/' + name + '.tar.gz',
                              tmp_dest_file)
                

    def create_db_config_map(self, q):
        DEFAULT_DB_ATTRS['INV_TIME_ZONE'] =  str(q.timezone)
        DEFAULT_DB_ATTRS['INV_NTP_ON'] = str(q.ntp_on)
        DEFAULT_DB_ATTRS['INV_NTP_SERVERS'] = str(q.ntp_servers)
        DEFAULT_DB_ATTRS['INV_PROXY_ON'] = str(q.proxy_on)
        DEFAULT_DB_ATTRS['INV_HTTP_PROXY'] = str(q.http_proxy)
        DEFAULT_DB_ATTRS['INV_HTTP_PROXY_PORT'] = str(q.http_proxy_port)
        DEFAULT_DB_ATTRS['INV_HTTPS_PROXY'] = str(q.https_proxy)
        DEFAULT_DB_ATTRS['INV_HTTPS_PROXY_PORT'] = str(q.https_proxy_port)
        DEFAULT_DB_ATTRS['INV_FTP_PROXY'] = str(q.ftp_proxy)
        DEFAULT_DB_ATTRS['INV_FTP_PROXY_PORT'] = str(q.ftp_proxy_port)
        DEFAULT_DB_ATTRS['INV_PHONE_HOME_ON'] = str(q.phone_home_on)
        DEFAULT_DB_ATTRS['INV_PHONE_HOME_REG'] = str(q.phone_home_reg)
        DEFAULT_DB_ATTRS['INV_PHONE_HOME_CHECKIN'] = str(q.phone_home_checkin)
        DEFAULT_DB_ATTRS['INV_LOCALE'] = str(q.locale)
        DEFAULT_DB_ATTRS['INV_SINGLE_USER_LOGIN'] = str(q.single_user_login)

        return DEFAULT_DB_ATTRS

    def create_dyn_config_map(self, mac):
        DEFAULT_DYN_ATTRS['INV_CONFIG_HOST'] =  socket.gethostname()
        DEFAULT_DYN_ATTRS['INV_CONFIG_HOST_TYPE'] =  'hub'
        DEFAULT_DYN_ATTRS['INV_HOSTNAME'] =  'station-' + mac

        return DEFAULT_DYN_ATTRS

    def return_initial_config_file(self, config_map):
        log.debug('return initial config file for name: ' + config_map['INV_HOSTNAME'])

        tmp_file_path = h.tmp_file_name(log)
        output = open(tmp_file_path, 'a+')
        properties = []

        properties.append('#Initial Configuration\n')

        for key, value in config_map.iteritems():
            properties.append(str(key) + '="' + h.escape_quotes(str(value)) + '"\n')
 
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

        map = self.create_dyn_config_map(mac_address)

        initialconfig_q = model.sac.query(model.Config).get_by(mac = mac_address)

        log.info('type : ' + str(type(initialconfig_q)))

        if str(type(initialconfig_q)) == NONE_TYPE: # this code stinks
            map.update(DEFAULT_DB_ATTRS)
        else:
            map.update(self.create_db_config_map(initialconfig_q))

        return self.return_initial_config_file(map)

    def save_user_config(self, id):
        log.debug('save user config for: ' + str(id))
        return self.save_config_file(request, id, 'user')

    def save_station_config(self, id):
        log.debug('save station config for: ' + str(id))
        return self.save_config_file(request, id, 'station')

    def save_station_initial_config(self, id):
        log.debug('save station initial config')

        if not h.does_parameter_exist(request, 'config_file', log):
            log.error('No config file found')
            return

        config_file = request.POST['config_file']
        
        map = {}

        if config_file.file:
            while 1:
                line = config_file.file.readline()
                items = line.split("=")
                log.info(items)
                if items.count == 2:
                    map[items[0]] = items[1]
                                
                log.info(line)
                if not line: break
        
        log.info("looking up record " + str(id))
        newconfig_q = model.sac.query(model.Config).get(id)

        #newconfig_q.mac = str(id)
        newconfig_q.timezone = map['INV_TIME_ZONE']
        newconfig_q.ntp_on = map['INV_NTP_ON']
        newconfig_q.ntp_servers = map['INV_NTP_SERVERS']
        newconfig_q.proxy_on = map['INV_PROXY_ON']
        newconfig_q.http_proxy = map['INV_HTTP_PROXY']
        newconfig_q.http_proxy_port = map['INV_HTTP_PROXY_PORT']
        newconfig_q.https_proxy = map['INV_HTTPS_PROXY']
        newconfig_q.https_proxy_port = map['INV_HTTPS_PROXY_PORT']
        newconfig_q.ftp_proxy = map['INV_FTP_PROXY']
        newconfig_q.ftp_proxy_port = map['INV_FTP_PROXY_PORT']
        newconfig_q.phone_home_on = map['INV_PHONE_HOME_ON']
        newconfig_q.phone_home_reg = map['INV_PHONE_HOME_REG']
        newconfig_q.phone_home_checkin = map['INV_PHONE_HOME_CHECKIN']
        newconfig_q.locale = map['INV_LOCALE']
        newconfig_q.single_user_login = map['INV_SINGLE_USER_LOGIN']
        model.sac.session.flush()


        
        return 'save station initial config'
