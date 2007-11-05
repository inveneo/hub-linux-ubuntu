import sqlalchemy as sqla
from sqlalchemy.orm import mapper
from sacontext import PylonsSAContext

sac = PylonsSAContext()
sac.add_engine_from_config(None)

configs_table = sqla.Table('configs', sac.metadata,
    sqla.Column('id', sqla.Integer, primary_key=True),
    sqla.Column('mac', sqla.String(255)),
    sqla.Column('timezone', sqla.String(255)),
    sqla.Column('ntp_on', sqla.Boolean),
    sqla.Column('ntp_servers', sqla.String(255)),
    sqla.Column('proxy_on', sqla.Boolean),
    sqla.Column('http_proxy', sqla.String(255)),
    sqla.Column('http_proxy_port', sqla.Integer),
    sqla.Column('https_proxy', sqla.String(255)),
    sqla.Column('https_proxy_port', sqla.Integer),
    sqla.Column('ftp_proxy', sqla.String(255)),
    sqla.Column('ftp_proxy_port', sqla.Integer),
    sqla.Column('phone_home_on', sqla.Boolean),
    sqla.Column('phone_home_reg', sqla.String(255)),
    sqla.Column('phone_home_checkin', sqla.String(255)),    
    sqla.Column('locale', sqla.String(255)),
    sqla.Column('single_user_login', sqla.Boolean)
)

class Config(object):
    def __str__(self):
        return self.title
    
mapper(Config, configs_table, extension=sac.ext)

