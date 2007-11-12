from pylons import config
from sqlalchemy import Column, MetaData, Table, types
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm import scoped_session, sessionmaker

# Global session manager.  Session() returns the session object
# appropriate for the current web request.
Session = scoped_session(sessionmaker(autoflush=True, transactional=True,
                                      bind=config['pylons.g'].sa_engine))

# Global metadata. If you have multiple databases with overlapping table
# names, you'll need a metadata for each database.
metadata = MetaData()

# configuration table
configs_table = Table('configs', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('mac', types.String(255), unique=True),
    Column('timezone', types.String(255)),
    Column('ntp_on', types.Boolean),
    Column('ntp_servers', types.String(255)),
    Column('proxy_on', types.Boolean),
    Column('http_proxy', types.String(255)),
    Column('http_proxy_port', types.Integer),
    Column('https_proxy', types.String(255)),
    Column('https_proxy_port', types.Integer),
    Column('ftp_proxy', types.String(255)),
    Column('ftp_proxy_port', types.Integer),
    Column('phone_home_on', types.Boolean),
    Column('phone_home_reg', types.String(255)),
    Column('phone_home_checkin', types.String(255)),    
    Column('locale', types.String(255)),
    Column('single_user_login', types.Boolean)
)

class Config(object):
    def __str__(self):
        return self.title
    
mapper(Config, configs_table)

# servers table
servers_table = Table('servers', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('name', types.String(255), default="Inveneon"),
    Column('server_on', types.Boolean, default=True),
)

class Server(object):
    def __str__(self):
        return self.title
    
mapper(Server, servers_table)

# servers table
stations_table = Table('stations', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('mac', types.String(255), default="Inveneon"),
    Column('station_on', types.Boolean, default=True),
)

class Station(object):
    def __str__(self):
        return self.title
    
mapper(Station, stations_table)
