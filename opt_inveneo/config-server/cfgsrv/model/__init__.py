from pylons import config
from sqlalchemy import Column, MetaData, Table, types
from sqlalchemy.orm import mapper
from sqlalchemy.orm import scoped_session, sessionmaker

g = config['pylons.g']
h = config['pylons.h']

# Global session manager.  Session() returns the session object
# appropriate for the current web request.
Session = scoped_session(sessionmaker(autoflush=True, transactional=True,
                                          bind=g.sa_engine))

# Global metadata. If you have multiple databases with overlapping table
# names, you'll need a metadata for each database.
metadata = MetaData()

# station configuration table
station_table = Table('station', metadata,
    Column('mac', types.String(12), primary_key=True),
    Column('on', types.Boolean),
    Column('hostname', types.String(255)),
    Column('language', types.String(255)),
    Column('time_zone', types.String(255)),
    Column('ntp_on', types.Boolean),
    Column('ntp_servers', types.String(255)),
    Column('config_host', types.String(255)),
    Column('config_host_type', types.String(255)),
    Column('proxy_on', types.Boolean),
    Column('http_proxy', types.String(255)),
    Column('http_proxy_port', types.Integer),
    Column('https_proxy', types.String(255)),
    Column('https_proxy_port', types.Integer),
    Column('ftp_proxy', types.String(255)),
    Column('ftp_proxy_port', types.Integer),
    Column('local_user_docs_dir_on', types.Boolean),
    Column('local_shared_docs_dir_on', types.Boolean),
    Column('hub_docs_dirs_on', types.Boolean),
    Column('phone_home_on', types.Boolean),
    Column('phone_home_reg_url', types.String(255)),
    Column('phone_home_checkin_url', types.String(255)),
    Column('phone_home_latitude', types.String(255)),
    Column('phone_home_longitude', types.String(255))
)

class Station(object):

    def __init__(self, mac='000000000000'):
        """create a default station with given MAC address"""
        self.mac = mac
        self.on = False
        self.hostname = g.DEFAULT_STATION
        self.language = 'en_US.UTF-8'
        self.time_zone = 'US/Pacific'
        self.ntp_on = True
        self.ntp_servers = g.DEFAULT_SERVER + ':pool.ntp.org:ntp.ubuntu.com'
        self.config_host = g.DEFAULT_SERVER
        self.config_host_type = 'hub'
        self.proxy_on = False
        self.http_proxy = g.DEFAULT_SERVER
        self.http_proxy_port = 80
        self.https_proxy = g.DEFAULT_SERVER
        self.https_proxy_port = 443
        self.ftp_proxy = g.DEFAULT_SERVER
        self.ftp_proxy_port = 21
        self.local_user_docs_dir_on = False
        self.local_shared_docs_dir_on = False
        self.hub_docs_dirs_on = True
        self.phone_home_on = False
        self.phone_home_reg_url = \
                'http://community.inveneo.org/phone_home/register'
        self.phone_home_checkin_url = \
                'http://community.inveneo.org/phone_home/phone_home'
        self.phone_home_latitude = ''
        self.phone_home_longitude = ''

    def update(self, d):
        """update state according to dictionary values"""
        # XXX validate values
        for key, value in d.iteritems():
            if key == 'INV_HOSTNAME':
                self.hostname = value
            elif key == 'INV_LANG' or key == 'INV_LANGUAGE':
                self.language = value
            elif key == 'INV_TIME_ZONE':
                # XXX this needs to be in the right format
                self.time_zone = value
            elif key == 'INV_NTP_ON':
                self.ntp_on = h.is_true(value)
            elif key == 'INV_NTP_SERVERS':
                self.ntp_servers = value
            elif key == 'INV_CONFIG_HOST':
                self.config_host = value
            elif key == 'INV_CONFIG_HOST_TYPE':
                self.config_host_type = value
            elif key == 'INV_PROXY_ON':
                self.proxy_on = h.is_true(value)
            elif key == 'INV_HTTP_PROXY':
                self.http_proxy = value
            elif key == 'INV_HTTP_PROXY_PORT':
                self.http_proxy_port = int(value)
            elif key == 'INV_HTTPS_PROXY':
                self.https_proxy = value
            elif key == 'INV_HTTPS_PROXY_PORT':
                self.https_proxy_port = int(value)
            elif key == 'INV_FTP_PROXY':
                self.ftp_proxy = value
            elif key == 'INV_FTP_PROXY_PORT':
                self.ftp_proxy_port = int(value)
            elif key == 'INV_LOCAL_USER_DOCS_DIR_ON':
                self.local_user_docs_dir_on = h.is_true(value)
            elif key == 'INV_LOCAL_SHARED_DOCS_DIR_ON':
                self.local_shared_docs_dir_on = h.is_true(value)
            elif key == 'INV_HUB_DOCS_DIRS_ON':
                self.hub_docs_dirs_on = h.is_true(value)
            elif key == 'INV_PHONE_HOME_ON':
                self.phone_home_on = h.is_true(value)
            elif key == 'INV_PHONE_HOME_REG_URL':
                self.phone_home_reg_url = value
            elif key == 'INV_PHONE_HOME_CHECKIN_URL':
                self.phone_home_checkin_url = value
            elif key == 'INV_PHONE_HOME_LATITUDE':
                self.phone_home_latitude = value
            elif key == 'INV_PHONE_HOME_LONGITUDE':
                self.phone_home_longitude = value
            else:
                #raise Exception("Invalid Key: %s", key)
                pass

    def properties(self):
        """return _most_ object contents as a dictionary (all strings)"""
        d = {}
        d['INV_HOSTNAME'] = self.hostname
        d['INV_LANG'] = d['INV_LANGUAGE'] = self.language
        d['INV_TIME_ZONE'] = self.time_zone
        d['INV_NTP_ON'] = ['0', '1'][self.ntp_on]
        d['INV_NTP_SERVERS'] = self.ntp_servers
        d['INV_CONFIG_HOST'] = self.config_host
        d['INV_CONFIG_HOST_TYPE'] = self.config_host_type
        d['INV_PROXY_ON'] = ['0', '1'][self.proxy_on]
        d['INV_HTTP_PROXY'] = self.http_proxy
        d['INV_HTTP_PROXY_PORT'] = str(self.http_proxy_port)
        d['INV_HTTPS_PROXY'] = self.https_proxy
        d['INV_HTTPS_PROXY_PORT'] = str(self.https_proxy_port)
        d['INV_FTP_PROXY'] = self.ftp_proxy
        d['INV_FTP_PROXY_PORT'] = str(self.ftp_proxy_port)
        d['INV_LOCAL_USER_DOCS_DIR_ON'] = \
                ['no', 'yes'][self.local_user_docs_dir_on]
        d['INV_LOCAL_SHARED_DOCS_DIR_ON'] = \
                ['no', 'yes'][self.local_shared_docs_dir_on]
        d['INV_HUB_DOCS_DIRS_ON'] = \
                ['no', 'yes'][self.hub_docs_dirs_on]
        d['INV_PHONE_HOME_ON'] = ['no', 'yes'][self.phone_home_on]
        d['INV_PHONE_HOME_REG_URL'] = self.phone_home_reg_url
        d['INV_PHONE_HOME_CHECKIN_URL'] = self.phone_home_checkin_url
        d['INV_PHONE_HOME_LATITUDE'] = self.phone_home_latitude
        d['INV_PHONE_HOME_LONGITUDE'] = self.phone_home_longitude
        return d

    def clone(self, src):
        """copy all settings (except MAC) from given Station object"""
        self.on = src.on
        self.hostname = src.hostname
        self.language = src.language
        self.time_zone = src.time_zone
        self.ntp_on = src.ntp_on
        self.ntp_servers = src.ntp_servers
        self.config_host = src.config_host
        self.config_host_type = src.config_host_type
        self.proxy_on = src.proxy_on
        self.http_proxy = src.http_proxy
        self.http_proxy_port = src.http_proxy_port
        self.https_proxy = src.https_proxy
        self.https_proxy_port = src.https_proxy_port
        self.ftp_proxy = src.ftp_proxy
        self.ftp_proxy_port = src.ftp_proxy_port
        self.local_user_docs_dir_on = src.local_user_docs_dir_on
        self.local_shared_docs_dir_on = src.local_shared_docs_dir_on
        self.hub_docs_dirs_on = src.hub_docs_dirs_on
        self.phone_home_on = src.phone_home_on
        self.phone_home_reg_url = src.phone_home_reg_url
        self.phone_home_checkin_url = src.phone_home_checkin_url
        self.phone_home_latitude = src.phone_home_latitude
        self.phone_home_longitude = src.phone_home_longitude

    def __str__(self):
        """return object contents as string"""
        d = self.properties()
        d['mac'] = self.mac
        d['on'] = str(self.on)
        return str(d)

mapper(Station, station_table)

# servers table
servers_table = Table('servers', metadata,
    Column('name', types.String(255), primary_key=True),
    Column('server_on', types.Boolean)
)

class Server(object):

    def __init__(self, name):
        """set default values on new object"""
        self.name = name
        self.server_on = False

    def __str__(self):
        """return object contents as string"""
        s = ''
        s += 'id = %s, ' % str(self.id)
        s += 'name = %s, ' % str(self.name)
        s += 'server_on = %s, ' % str(self.server_on)
        return s

mapper(Server, servers_table)

# admins table
admins_table = Table('admins', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('login_name', types.String(255), unique=True),
    Column('first_name', types.String(255)),
    Column('last_name', types.String(255)),
    Column('password', types.String(255)),
    Column('salt', types.String(255))
)

class Admin(object):

    def __init__(self):
        """set default values on new object"""
        self.login_name = g.DEFAULT_ADMIN
        self.first_name = g.DEFAULT_ADMIN
        self.last_name = ''
        self.password = ''
        self.salt = 0

    def __str__(self):
        """return object contents as string"""
        s = ''
        s += 'id = %s, ' % str(self.id)
        s += 'login_name = %s, ' % str(self.login_name)
        s += 'first_name = %s, ' % str(self.first_name)
        s += 'last_name = %s, ' % str(self.last_name)
        s += 'password = %s, ' % str(self.password)
        s += 'salt = %s, ' % str(self.salt)
        return s

mapper(Admin, admins_table)

