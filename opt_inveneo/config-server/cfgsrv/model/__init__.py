from pylons import config
from sqlalchemy import Column, MetaData, Table, types
from sqlalchemy.orm import mapper
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
    Column('hostname', types.String(255)),
    Column('lang', types.String(255)),
    Column('time_zone', types.String(255)),
    Column('config_host', types.String(255)),
    Column('config_host_type', types.Integer),
    Column('proxy_on', types.Boolean),
    Column('ntp_on', types.Boolean),
    Column('ntp_servers', types.String(255)),
    Column('hub_docs_dirs_on', types.Boolean),
    Column('local_shared_docs_dir_on', types.Boolean),
    Column('local_user_docs_dir_on', types.Boolean),
    Column('phone_home_on', types.Boolean),
    Column('phone_home_reg', types.String(255)),
    Column('phone_home_checkin', types.String(255))
)

class Config(object):
    def __str__(self):
        return self.title

mapper(Config, configs_table)

# servers table
servers_table = Table('servers', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('name', types.String(255), default="inveneo"),
    Column('server_on', types.Boolean, default=True)
)

class Server(object):
    def __str__(self):
        return self.title

mapper(Server, servers_table)

# stations table
stations_table = Table('stations', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('mac', types.String(255)),
    Column('station_on', types.Boolean, default=True)
)

class Station(object):
    def __str__(self):
        return self.title

mapper(Station, stations_table)

# users table
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
        return self.title

mapper(Admin, admins_table)

