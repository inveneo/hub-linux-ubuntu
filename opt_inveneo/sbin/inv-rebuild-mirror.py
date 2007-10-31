#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import syslog
import traceback
import getopt
import subprocess as sp
import re
from os import path
from sys import stdout, stderr



def is_root_device_raid():
    try:
        root_dev = sp.Popen(["rdev"], stdout=sp.PIPE).communicate()[0].split()[0]
        sp.check_call(['mdadm','-D','--brief',root_dev]) # will throw exception if not a RAID device
    except Exception, ex:
        return False
    
    return True

def main():
    syslog.openlog('inv-rebuild-mirror', 0, syslog.LOG_LOCAL5)
    
    # if not a raided root device, return
    if not is_root_device_raid(): 
        stderr.write("Root device is not a RAID array\n")
        return 1

if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/opt/inveneo/bin:/opt/inveneo/sbin'
    sys.exit(main())