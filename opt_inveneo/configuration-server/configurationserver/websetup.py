"""Setup the configuration-server application"""
import logging

from paste.deploy import appconfig
from pylons import config

from configurationserver.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup testing here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    from configurationserver.lib.base import model
    print "Creating tables"
    model.sac.metadata.create_all()
    print "Successfully setup"
