#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import with_statement

import os
from os import path
import sys
import syslog
import traceback
import subprocess as sp

sys.path.append("/opt/inveneo/lib/python")


def main():
    syslog.openlog('install-hub-linux', 0, syslog.LOG_LOCAL5)
    install_root=path.dirname(path.dirname(path.abspath(sys.argv[0])))
    overlay_root=path.join(install_root, "overlay")

    print "\nRemoving and adding packages...\n"
    sp.check_call([path.join(install_root, 'bin','install-packages.py'),
                   path.join(install_root, 'package.d')])

    # TO DO: install ruby and overlay
    #
    
    return 0
        
                
if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    sys.exit(main())
