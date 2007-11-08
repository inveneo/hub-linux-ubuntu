"""Pylons environment configuration"""
from sqlalchemy import engine_from_config
from pylons import config
import os

import configurationserver.lib.app_globals as app_globals
import configurationserver.lib.helpers
from configurationserver.config.routing import make_map

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='configurationserver',
                    template_engine='mako', paths=paths)

    config['routes.map'] = make_map()
    config['pylons.h'] = configurationserver.lib.helpers
    config['pylons.g'] = app_globals.Globals()
    # SQLAlchemy 0.4
    config['pylons.g'].sa_engine = engine_from_config(config, 'sqlalchemy.')

    # Customize templating options via this variable
    tmpl_options = config['buffet.template_options']

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
