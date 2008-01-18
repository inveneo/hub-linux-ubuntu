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
    stations = model.Session.query(model.Station)
    station = stations.filter(model.Station.mac == g.DEFAULT_MAC).first()
    if station:
        print "Station already existing"
    else:
        station = model.Station(g.DEFAULT_MAC)
        model.Session.save(station)
        model.Session.commit()
        print "Successfully created default station"

    # Create default server
    print "Creating default server"
    servers = model.Session.query(model.Server)
    server = servers.filter(model.Server.name == g.DEFAULT_SERVER).first()
    if server:
        print "Server already existing"
    else:
        server = model.Server(g.DEFAULT_SERVER)
        model.Session.save(server)
        model.Session.commit()
        print "Successfully created default server"

    print "Setup finished"

