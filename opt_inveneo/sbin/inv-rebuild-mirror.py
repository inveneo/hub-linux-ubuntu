#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import with_statement

import os
import sys
import syslog
import traceback
import getopt
import subprocess as sp
import re
from os import path
from sys import stdout, stderr

MDADM_CONF='/etc/mdadm/mdadm.conf'
MDADM_STAT='/proc/mdstat'

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
 
def get_phys_drives_for_array(array_dev):
    result=[]
    array=array_dev.split('/')[-1] # convert /dev/mdX to mdX 
    drives=[]
    try:
        with open(MDADM_STAT) as f:
            for line in f:
                if line.startswith(array):
                    drives=line[len(array)+3:].split()[2:]
                    break
    except Exception, ex:
        traceback.print_exc(20, stdout)
        drives=[]
        
    for d in drives:
        result.append(d[:d.index('[')])
    
    return result

def main():
    syslog.openlog('inv-rebuild-mirror', 0, syslog.LOG_LOCAL5)
    
    # if not a raided root device, return
    if not is_root_device_raid(): 
        stderr.write("Root device is not a RAID array\n")
        return 1
        
    # parse mdadm.conf
    arrays=parse_mdadm_conf(MDADM_CONF)
    if len(arrays) == 0: 
        stderr.write("No arrays found in "+MDADM_CONF+"\n")
        return 2
    
    # see if _all_ are degraded and running on same physical disk
    # if _some_ are running on two disks, or any are running on
    # different disks, we do nothing
    all_degraded=True # assume degraded unless otherwise
    good_drive=None # set to physical drive that all arrays are using if all on the same
    for array in arrays.keys():
        if sp.call(['mdadm','-D','--brief','--test',array]) != 1:
            all_degraded=False
            break

        new_drive = get_phys_drives_for_array(array)[0]
        stdout.write('Drive: '+new_drive+"\n\n\n")
        if good_drive != None and ( good_drive != new_drive ):
            # mismatched drives!
            good_drive = None
            break
        else:
            good_drive = new_drive # in case first drive and good_drive is None
    
    if not all_degraded:
        stderr.write("Not all arrays degraded, doing nothing\n")
        return 0
        
    if good_drive == None:
        stderr.write("Arrays have physical drive mismatch--they are degraded but running on different drives. Doing nothing.\n")
        return 0
        
    # Ok, now we think we can do something, but we have to see if there is a drive we
    # can extend the arrays onto
        

if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/opt/inveneo/bin:/opt/inveneo/sbin'
    sys.exit(main())
