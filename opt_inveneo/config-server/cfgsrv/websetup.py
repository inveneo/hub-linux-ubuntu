"""Setup the cfgsrv application"""
import logging
import random
import crypt

from paste.deploy import appconfig
from pylons import config

from cfgsrv.lib.base import g
from cfgsrv.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
     """Place any commands to setup testing here"""
     conf = appconfig('config:' + filename)
     load_environment(conf.global_conf, conf.local_conf)
     from cfgsrv import model
     print "Creating tables"
     model.metadata.create_all(bind=config['pylons.g'].sa_engine)
     print "Successfully setup"
     create_default_admin()
     create_default_station()
     create_default_server()

def create_default_admin():
     from cfgsrv import model
     print "Creating default admin if not existing"
     try:
          model.Session.query(model.Admin).filter(model.Admin.login_name == 'root').one()
          print "Admin already existing"
     except:
          admin_q = model.Admin()
          admin_q.login_name = 'root'
          admin_q.first_name = 'root'
          admin_q.last_name = ''
          admin_q.salt = '1366'
          admin_q.password = '13Bfi/A0PbT4g'
          # admin_q.salt = str(random.randint(0, 99)) + str(random.randint(0, 99))
          # admin_q.password = crypt.crypt('<the usual>', admin_q.salt)
          model.Session.save(admin_q)
          model.Session.commit()
          print "Successfully created default admin"

def create_default_station():
     from cfgsrv import model
     from cfgsrv.controllers import admin
     print "Creating default station"
     try:
          model.Session.query(model.Config).filter(model.Config.mac == g.DEFAULT_MAC).one()
          print "Station already existing"
     except:
          newconfig_q = admin.Get_initial_config()          
          model.Session.save(newconfig_q)
          model.Session.commit()
          print "Successfully created default station"

def create_default_server():
     from cfgsrv import model
     print "Creating default 'inveneo' server"
     try:
          model.Session.query(model.Server).filter(model.Server.name == 'inveneo').one()
          print "Server already existing"
     except:
          s_q = model.Server()
          model.Session.save(s_q)
          model.Session.commit()
          print "Successfully created default server"

