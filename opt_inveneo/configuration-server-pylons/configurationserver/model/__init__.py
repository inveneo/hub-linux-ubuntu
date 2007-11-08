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
    Column('mac', types.String(255)),
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

# 0.3.1
#import sqlalchemy as sqla
#from sqlalchemy.orm import mapper
#from sacontext import PylonsSAContext
#
#sac = PylonsSAContext()
#sac.add_engine_from_config(None)
#
# configs_table = sqla.Table('configs', sac.metadata,
#     sqla.Column('id', sqla.Integer, primary_key=True),
#     sqla.Column('mac', sqla.String(255)),
#     sqla.Column('timezone', sqla.String(255)),
#     sqla.Column('ntp_on', sqla.Boolean),
#     sqla.Column('ntp_servers', sqla.String(255)),
#     sqla.Column('proxy_on', sqla.Boolean),
#     sqla.Column('http_proxy', sqla.String(255)),
#     sqla.Column('http_proxy_port', sqla.Integer),
#     sqla.Column('https_proxy', sqla.String(255)),
#     sqla.Column('https_proxy_port', sqla.Integer),
#     sqla.Column('ftp_proxy', sqla.String(255)),
#     sqla.Column('ftp_proxy_port', sqla.Integer),
#     sqla.Column('phone_home_on', sqla.Boolean),
#     sqla.Column('phone_home_reg', sqla.String(255)),
#     sqla.Column('phone_home_checkin', sqla.String(255)),    
#     sqla.Column('locale', sqla.String(255)),
#     sqla.Column('single_user_login', sqla.Boolean)
# )

# class Config(object):
#     def __str__(self):
#         return self.title
    
# mapper(Config, configs_table, extension=sac.ext)

