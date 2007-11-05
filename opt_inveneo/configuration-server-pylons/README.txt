This file is for you to describe the configuration-server application. Typically
you would include information such as the information below:

Installation and Setup
======================

Install ``configuration-server`` using easy_install::

    easy_install configuration-server

Make a config file as follows::

    paster make-config configuration-server config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go.
