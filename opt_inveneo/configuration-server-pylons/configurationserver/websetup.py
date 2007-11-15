"""Setup the configuration-server application"""
import logging
import random
import crypt

from paste.deploy import appconfig
from pylons import config

from configurationserver.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
     """Place any commands to setup testing here"""
     conf = appconfig('config:' + filename)
     load_environment(conf.global_conf, conf.local_conf)
     from configurationserver import model
     print "Creating tables"
     model.metadata.create_all(bind=config['pylons.g'].sa_engine)
     print "Successfully setup"
     print "Creating default user if not existing"
     try:
        model.Session.query(model.User).filter(model.User.login_name == 'Inveneo').one()
        print "User already existing"
     except:
          user_q = model.User()
          user_q.login_name = 'Inveneo'
          user_q.first_name = 'Inveneo'
          user_q.last_name = ''
          user_q.salt = str(random.randint(0, 99)) + str(random.randint(0, 99))
          user_q.password = crypt.crypt('1nvene0', user_q.salt)
          model.Session.save(user_q)
          model.Session.commit()
          print "Successfully created default user"


