from pylons import config
from sqlalchemy import Column, MetaData, Table, types
from sqlalchemy.orm import mapper
from sqlalchemy.orm import scoped_session, sessionmaker

g = config['pylons.g']

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

    def __init__(self, mac):
        """set default values on new config"""
        self.mac = mac
        self.on = True
        #INV_HOSTNAME
        self.hostname = g.DEFAULT_STATION
        #INV_LANG and INV_LANGUAGE
        self.language = 'en_US.UTF-8'
        #INV_TIME_ZONE
        self.time_zone = 'US/Pacific'
        #INV_NTP_ON
        self.ntp_on = True
        #INV_NTP_SERVERS
        self.ntp_servers = g.DEFAULT_SERVER + ':pool.ntp.org:ntp.ubuntu.com'
        #INV_CONFIG_HOST
        self.config_host = g.DEFAULT_SERVER
        #INV_CONFIG_HOST_TYPE
        self.config_host_type = 'hub'
        #INV_PROXY_ON
        self.proxy_on = False
        #INV_HTTP_PROXY
        self.http_proxy = g.DEFAULT_SERVER
        #INV_HTTP_PROXY_PORT
        self.http_proxy_port = 80
        #INV_HTTPS_PROXY
        self.https_proxy = g.DEFAULT_SERVER
        #INV_HTTPS_PROXY_PORT
        self.https_proxy_port = 443
        #INV_FTP_PROXY
        self.ftp_proxy = g.DEFAULT_SERVER
        #INV_FTP_PROXY_PORT
        self.ftp_proxy_port = 21
        #INV_LOCAL_USER_DOCS_DIR_ON
        self.local_user_docs_dir_on = False
        #INV_LOCAL_SHARED_DOCS_DIR_ON
        self.local_shared_docs_dir_on = False
        #INV_HUB_DOCS_DIRS_ON
        self.hub_docs_dirs_on = True
        #INV_PHONE_HOME_ON
        self.phone_home_on = False
        #INV_PHONE_HOME_REG_URL
        self.phone_home_reg_url = \
                'http://community.inveneo.org/phone_home/register'
        #INV_PHONE_HOME_CHECKIN_URL
        self.phone_home_checkin_url = \
                'http://community.inveneo.org/phone_home/phone_home'
        #INV_PHONE_HOME_LATITUDE
        self.phone_home_latitude = ''
        #INV_PHONE_HOME_LONGITUDE
        self.phone_home_longitude = ''

    def __str__(self):
        """return object contents as string"""
        s = ''
        s += 'mac = %s, ' % str(self.mac)
        s += 'on = %s, ' % str(self.on)
        s += 'hostname = %s, ' % str(self.hostname)
        s += 'language = %s, ' % str(self.language)
        s += 'time_zone = %s, ' % str(self.time_zone)
        s += 'ntp_on = %s, ' % str(self.ntp_on)
        s += 'ntp_servers = %s, ' % str(self.ntp_servers)
        s += 'config_host = %s, ' % str(self.config_host)
        s += 'config_host_type = %s, ' % str(self.config_host_type)
        s += 'proxy_on = %s, ' % str(self.proxy_on)
        s += 'http_proxy = %s, ' % str(self.http_proxy)
        s += 'http_proxy_port = %s, ' % str(self.http_proxy_port)
        s += 'https_proxy = %s, ' % str(self.https_proxy)
        s += 'https_proxy_port = %s, ' % str(self.https_proxy_port)
        s += 'ftp_proxy = %s, ' % str(self.ftp_proxy)
        s += 'ftp_proxy_port = %s, ' % str(self.ftp_proxy_port)
        s += 'local_user_docs_dir_on = %s, ' % str(self.local_user_docs_dir_on)
        s += 'local_shared_docs_dir_on = %s, ' % \
                str(self.local_shared_docs_dir_on)
        s += 'hub_docs_dirs_on = %s, ' % str(self.hub_docs_dirs_on)
        s += 'phone_home_on = %s, ' % str(self.phone_home_on)
        s += 'phone_home_reg_url = %s, ' % str(self.phone_home_reg_url)
        s += 'phone_home_checkin_url = %s, ' % str(self.phone_home_checkin_url)
        s += 'phone_home_latitude = %s, ' % str(self.phone_home_latitude)
        s += 'phone_home_longitude = %s, ' % str(self.phone_home_longitude)
        return s

mapper(Station, station_table)

# servers table
servers_table = Table('servers', metadata,
    Column('name', types.String(255), primary_key=True),
    Column('server_on', types.Boolean, default=True)
)

class Server(object):

    def __init__(self, name):
        """set default values on new config"""
        self.name = name
        self.server_on = True

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
    def __str__(self):
        return str(type(self))

mapper(Admin, admins_table)

