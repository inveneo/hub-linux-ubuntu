#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import syslog
import traceback
import shutil
import subprocess as sp
from os import path
from sys import stdout, stderr

def main():
    syslog.openlog('pre-image-clean', 0, syslog.LOG_LOCAL5)
    
    install_root=path.dirname(path.dirname(path.abspath(sys.argv[0])))
    overlay_root=path.join(install_root, "overlay")
    install_bin=path.join(install_root, 'bin')

    stdout.write("\nRemoving udev NIC naming rules...\n")
    try:
        os.remove('/etc/udev/rules.d/70-persistent-net.rules')
    except Exception, ex:
        pass # ignore if not there

    # remove any lock files that might block rule regeneration
    shutil.rmtree('/dev/.udev/.lock-70-persistent-net.rules', True)

    stdout.write("\nUpdating APT and clearing APT cache...\n")
    sp.call(['apt-get','update'])
    sp.call(['apt-get','clean'])
        
    return 0
                
if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    sys.exit(main())
