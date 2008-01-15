"""Setup the cfgsrv application"""
import logging
import random
import crypt

from paste.deploy import appconfig
from pylons import config

from cfgsrv.config.environment import load_environment

log = logging.getLogger(__name__)

SALT = '1366'

def setup_config(command, filename, section, vars):
    """Place any commands to setup testing here"""
    print "Setup beginning"
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    g = config['pylons.g']

    # Populate the DB on 'paster setup-app'
    import cfgsrv.model as model

    print "Setting up database connectivity..."
    engine = g.sa_engine

    print "Creating tables..."
    model.metadata.create_all(bind=engine)

    # Create default administrator
    print "Creating default admin if not existing"
    try:
        q = model.Session.query(model.Admin)
        q.filter(model.Admin.login_name == 'root').one()
        print "Admin already existing"
    except:
        admin_q = model.Admin()
        admin_q.login_name = 'inveneo'
        admin_q.first_name = 'Inveneo'
        admin_q.last_name = 'Administrator'
        admin_q.salt = SALT
        admin_q.password = crypt.crypt('1nvene0', SALT)
        # admin_q.salt = str(random.randint(0, 99)) + str(random.randint(0, 99))
        # admin_q.password = crypt.crypt('<the usual>', admin_q.salt)
        model.Session.save(admin_q)
        model.Session.commit()
        print "Successfully created default admin"

    # Create default station
    print "Creating default station"
    try:
        q = model.Session.query(model.Config)
        q.filter(model.Config.mac == g.DEFAULT_MAC).one()
        print "Station already existing"
    except:
        station = model.Config()
        station.mac = str(g.DEFAULT_MAC)
        station.lang = g.DEFAULT_DB_ATTRS['INV_LANG']
        station.time_zone = g.DEFAULT_DB_ATTRS['INV_TIME_ZONE']
        station.config_host = g.DEFAULT_DB_ATTRS['INV_CONFIG_HOST']
        station.config_host_type = g.DEFAULT_DB_ATTRS['INV_CONFIG_HOST_TYPE']
        station.proxy_on = g.DEFAULT_DB_ATTRS['INV_PROXY_ON']
        station.ntp_on = g.DEFAULT_DB_ATTRS['INV_NTP_ON']
        station.ntp_servers = g.DEFAULT_DB_ATTRS['INV_NTP_SERVERS']
        station.hub_docs_dirs_on = g.DEFAULT_DB_ATTRS['INV_HUB_DOCS_DIRS_ON']
        station.local_shared_docs_dir_on = \
                g.DEFAULT_DB_ATTRS['INV_LOCAL_SHARED_DOCS_DIR_ON']
        station.local_user_docs_dir_on = \
                g.DEFAULT_DB_ATTRS['INV_LOCAL_USER_DOCS_DIR_ON']
        station.phone_home_on = g.DEFAULT_DB_ATTRS['INV_PHONE_HOME_ON']
        station.phone_home_reg_url = \
                g.DEFAULT_DB_ATTRS['INV_PHONE_HOME_REG_URL']
        station.phone_home_checkin_url = \
                g.DEFAULT_DB_ATTRS['INV_PHONE_HOME_CHECKIN_URL']
        model.Session.save(station)
        model.Session.commit()
        print "Successfully created default station"

    # Create default server
    print "Creating default server"
    try:
        q = model.Session.query(model.Server)
        q.filter(model.Server.name == 'inveneo').one()
        print "Server already existing"
    except:
        s_q = model.Server()
        model.Session.save(s_q)
        model.Session.commit()
        print "Successfully created default server"

    print "Setup finished"

