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
PARTITIONS='/proc/partitions'
MOUNTS='/proc/mounts'

def device_to_drive(device):
    """converts stuff of form /dev/sda1 to sda"""
    return strip_partition(device.split('/')[-1])

part_stripper=re.compile('^(.+?)[0-9]*$')
def strip_partition(drive):
    return part_stripper.match(drive).groups()[0]

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

udev_id_bus_matcher=re.compile(r'^ID_BUS=(.+)$',re.M)
def is_scsi(dev):
    """is the device really scsi or is it USB hiding as scsi?"""
    udev_out=sp.Popen(['udevinfo','--query=env','--name='+dev],stdout=sp.PIPE).communicate()[0]
    
    match=udev_id_bus_matcher.search(udev_out)
    return match and match.groups()[0]=='scsi'

disk_size_matcher=re.compile(r'^Disk.+:\s([0-9]+)MB$',re.M)
def disk_size_mb(drive):
    # TODO: can I just read /sys/block/<dev>/size and assume always in 512 units?
    drive='/dev/'+drive
    out = sp.Popen(['parted',drive,'unit','MB','print'],stdout=sp.PIPE).communicate()[0]
    size = int(disk_size_matcher.search(out).groups()[0])
    return size
    
def drive_in_use(raw_drive):
    """True if drive is mounted (in /proc/mounts) or in an array (appears in /proc/mdstat)"""
    
    # check mounts
    try:
       with open(MOUNTS) as f:
           pat=re.compile(r'^.+'+raw_drive+r'[0-9]*\s')
           for line in f:
               if pat.match(line): return True
    except Exception, ex:
        traceback.print_exc(20, stdout)
        pass
    
    # check arrays
    try:
       with open(MDADM_STAT) as f:
           pat=re.compile(r'\s'+raw_drive+r'[0-9]*\[')
           for line in f:
               if pat.search(line): return True
    except Exception, ex:
        traceback.print_exc(20, stdout)
        pass    
        
    return False

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

        new_drive = strip_partition(get_phys_drives_for_array(array)[0])
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
        
    # Ok, now we think we can do something, but we have to see 
    # if there is a drive we can extend the arrays onto
    good_device='/dev/'+good_drive
    target_device=None
    
    # we _assume_ that we are a two disk system, so we look for a valid drive
    # where mdadm.conf expects it, we just have to look at an array entry
    # and pick the drive that _isn't_ currently in use
    for dev in arrays[arrays.keys()[0]]:
        if not dev.startswith(good_device):
            target_device = strip_partition(dev)
            break
    
    if target_device == None:
        stderr.write('Could not find second device for mirror in mdadm.conf.\nDoing nothing.\n')
        return 2
        
    target_drive=device_to_drive(target_device)
    
    # now see if we have the drive and if it matches our criteria
    good_drive_size=disk_size_mb(good_drive)
    if not ( \
        is_scsi(target_drive) and \
        disk_size_mb(target_drive)>=good_drive_size and \
        not drive_in_use(target_drive) \
        ): 
        stderr.write("Drive: "+target_drive+" not found or not usable\n")
        return 2

    stdout.write("Will add '"+target_drive+"' to mirror\n")
    # first trash any superblocks that might confuse mdadm
    with open(PARTITIONS) as f:
        for l in f:
            dev=l.split()
            if len(dev)==4 and \
                dev[3].startswith(target_drive):
                stdout.write("Zeroing any superblock on: "+dev[3]+"\n")
                sp.call(['mdadm','--zero-superblock','/dev/'+dev[3]])
    
    # now copy over the partition table from the good drive
    stdout.write("Copying partition table to: "+target_device+"\n")
    dump = sp.Popen(['sfdisk','-d',good_device], stdout=sp.PIPE)
    sp.Popen(['sfdisk', target_device], stdin=dump.stdout, stdout=sp.PIPE).communicate()
    
    # verify tables are the same now
    orig = sp.Popen(['sfdisk','-d',good_device],stdout=sp.PIPE).communicate()[0].split('\n\n')[1].replace(good_device, '/dev/block')
    new = sp.Popen(['sfdisk','-d',target_device],stdout=sp.PIPE).communicate()[0].split('\n\n')[1].replace(target_device,'/dev/block')

    if new != orig:
        stderr.write("Oops. Just wrote partition table on: "+target_device+\
        " and it doesn't match original table so I can't use the drive\n")
        return 2
        
    # now the MBR
    stdout.write("Copying MBR\n")
    sp.call(['dd','if='+good_device,'of='+target_device,'bs=512','count=1'])
    
    # now add the drives to the array
    for array in arrays.keys():
        for part in arrays[array]:
            if not part.startswith(good_device):
                stdout.write("Adding '"+part+"' to array '"+array+"'\n")
                sp.call(['mdadm','--add',array,part])
                break

    
    

if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/opt/inveneo/bin:/opt/inveneo/sbin'
    sys.exit(main())
