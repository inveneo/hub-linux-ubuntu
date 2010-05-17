#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import syslog
import traceback
import subprocess as sp
from os import path
from sys import stdout, stderr, stdin

def main():
    syslog.openlog('install-hub-linux', 0, syslog.LOG_LOCAL5)
    
    install_root=path.dirname(path.dirname(path.abspath(sys.argv[0])))
    overlay_root=path.join(install_root, "overlay")
    install_bin=path.join(install_root, 'bin')

    stdout.write("\nRemoving and adding packages...\n")
    sp.check_call([path.join(install_bin,'install-packages.py'),
                   path.join(install_root, 'package.d')])
    
    stdout.write("\nInstalling Hub Overlay...\n")
    sp.check_call([path.join(install_bin,'install-hub-overlay.py')])
    
    stdout.write("\nPopulating LDAP server...\n")
    sp.check_call([path.join(install_bin,'populate-hub-ldap.py')])
    
    
    stdout.write("\nHit any key to reboot--you really need to...\n")
    stdin.readline()
    os.system("reboot")
        
    return 0
        
                
if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    sys.exit(main())
