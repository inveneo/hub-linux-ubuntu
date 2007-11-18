#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
install-hub-overlay.py

Created by Jeff Wishnie on 2007-10-03.
Copyright (c) 2007 Inveneo, inc. All rights reserved.
"""

from __future__ import with_statement

import os
import sys
import syslog
import traceback
import re
import pwd
import subprocess as sp
from os import path
from sys import stderr,stdout

def svn_update(to_update):
    """docstring for svn_update"""
    sp.check_call(['svn','update',to_update])
    
def main():
    syslog.openlog('update-hub-overlay', 0, syslog.LOG_LOCAL5)
    
    # get useful paths
    install_root=path.dirname(path.dirname(path.abspath(sys.argv[0])))
    opt_root=path.dirname(install_root)
    opt_inveneo=path.join(opt_root,'inveneo')
    
    stdout.write('\nUpdating: '+install_root+'...\n')
    svn_update(install_root)
    
    stdout.write('\nUpdating: '+opt_inveneo+'...\n')
    svn_update(opt_inveneo)
    
    stdout.write("\nInstalling any new packages...\n")
    sp.call([path.join(install_root,'bin','install-packages.py'),path.join(install_root,'package.d')])
    
    stdout.write('\nReinstalling overlay...\n')
    sp.call([path.join(install_root,'bin','install-hub-overlay.py')])

    stdout.write('\nRepopulating Samba...\n')
    sp.call([path.join(install_root,'bin','populate-hub-ldap.py')])
    
    return 0

if __name__ == '__main__':
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    sys.exit(main())

