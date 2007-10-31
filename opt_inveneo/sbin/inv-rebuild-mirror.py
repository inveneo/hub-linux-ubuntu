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

from __future__ import with_statement

MDADM_CONF='/etc/mdadm/mdadm.conf'

def is_root_device_raid():
    try:
        root_dev = sp.Popen(["rdev"], stdout=sp.PIPE).communicate()[0].split()[0]
        sp.check_call(['mdadm','-D','--brief',root_dev]) # will throw exception if not a RAID device
    except Exception, ex:
        return False
    
    # if we get here, it was a RAID array
    return True


conf_line_matcher=re.compile(r'^ARRAY\s(.+?)\s.*devices=(.+)[\s$]')
def parse_mdadm_conf(conf):
    result = {}
    try:
        with open(conf) as f:
            for line in f:
                match=conf_line_matcher.match(line)
                if match:
                    array, devices = match.groups()
                    result[array] = devices.split(',')
    except Exception, ex:
        result={}
    
    return result

def main():
    syslog.openlog('inv-rebuild-mirror', 0, syslog.LOG_LOCAL5)
    
    # if not a raided root device, return
    if not is_root_device_raid(): 
        stderr.write("Root device is not a RAID array\n")
        return 1
        
    # parse mdadm.conf
    arrays=parse_mdadm_conf(MDADM_CONF)
    stdout.write(str(arrays))

if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/opt/inveneo/bin:/opt/inveneo/sbin'
    sys.exit(main())