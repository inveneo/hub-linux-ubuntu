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
sys.path.append('/opt/inveneo/lib/python')
from inveneo import constants, fileutils

def main():
    syslog.openlog('pre-image-clean', 0, syslog.LOG_LOCAL5)
    
    install_root=path.dirname(path.dirname(path.abspath(sys.argv[0])))
    overlay_root=path.join(install_root, "overlay")
    install_bin=path.join(install_root, 'bin')

    stdout.write("\nRemoving hub certs and keys...\n")
    fileutils.safe_delete_node(constants.INV_HUB_CERTS_PATH)

    stdout.write("\nRemoving udev NIC naming rules...\n")
    fileutils.safe_delete_node('/etc/udev/rules.d/70-persistent-net.rules')

    # remove any lock files that might block rule regeneration
    fileutils.safe_delete_node('/dev/.udev/.lock-70-persistent-net.rules')

    stdout.write("\nClearing APT cache...\n")
    sp.call(['apt-get','autoremove'])
    sp.call(['apt-get','autoclean'])
    sp.call(['apt-get','clean'])
        
    return 0
                
if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    sys.exit(main())
