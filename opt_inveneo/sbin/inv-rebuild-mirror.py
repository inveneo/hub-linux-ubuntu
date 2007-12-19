#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

GRUB='/usr/sbin/grub'

# hash keys
DEGRADED='degraded'
PARTITIONS_IN_CONF='configured_drives' # drives found in mdadm.conf
PARTITIONS_IN_USE='in_use_drives' # drives actually active and in the array
IS_SWAP='is_swap'

# compiled regexes
part_stripper=re.compile('^(.+?)[0-9]*$')
conf_line_matcher=re.compile(r'^ARRAY\s(.+?)\s.*devices=(.+)[\s$]')
udev_id_bus_matcher=re.compile(r'^ID_BUS=(.+)$',re.M)
mdadm_detail_drive_matcher=re.compile(r'(?:active|rebuilding)\s(?:\S+)*\s+(\S+)$',re.M)

def device_to_part(device):
    """converts form /dev/sda1 to sda1"""
    return device.split('/')[-1]

def device_to_drive(device):
    """converts stuff of form /dev/sda1 to sda"""
    return strip_partition(device_to_part(device))

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


def parse_mdadm_conf(conf):
    result = {}
    try:
        with open(conf) as f:
            for line in f:
                match=conf_line_matcher.match(line)
                if match:
                    array, devices = match.groups()
                    result[array] = {} # make the entry a hash
                    result[array][PARTITIONS_IN_CONF] = map(device_to_part, devices.split(','))
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

def is_scsi(dev):
    """is the device really scsi or is it USB hiding as scsi?"""
    udev_out=sp.Popen(['udevinfo','--query=env','--name='+dev],stdout=sp.PIPE).communicate()[0]
    
    match=udev_id_bus_matcher.search(udev_out)
    return match and match.groups()[0]=='scsi'

def disk_size_mb(raw_drive):
    # TODO: is /sys/block/<dev>/size always same units for all drives?
    size_str="0"
    try:
        with open('/sys/block/'+raw_drive+'/size') as f:
            size_str=f.read().strip()
    except Exception, ex:
        size_str='0'

    return int(size_str)
    
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
    
def write_msg(msg, console=stdout):
    syslog.syslog(msg)
    console.write(msg+"\n")

def part_tables_same(dev1,dev2):
    # get dump of sfdisk for each, split output into
    # header and part table body (on double-new line), replace device specifics, eg /dev/sda
    # with /dev/block, and do string compare
    blank_dev='/dev/blank'

    output=[]
    for dev in ( dev1, dev2 ):
        output.append(sp.Popen(['sfdisk','-d',dev],stdout=sp.PIPE).communicate()[0].\
               split('\n\n')[1].replace(dev, blank_dev))
 
    return output[0] == output[1]

def add_drive_to_mirror(arrays_hash):
    # first we need to confirm that all the arrays are running on _one_ physical drive
    active_drive=None
    for key in arrays_hash.keys():
        array=arrays_hash[key]
        num_drives=len(array[PARTITIONS_IN_USE])

        if num_drives<1:
            write_msg("No active drives in array %s. Can't continue" % key)
            return 10
        elif num_drives>1:
            write_msg("Stopping: All drives should be degraded but array %s has multiple active drives: %s, perhaps it's rebuilding" %\
                      (key, str(array[PARTITIONS_IN_USE])))
            return 20

        # ok, we have exactly one drive
        cur_active_drive=strip_partition(array[PARTITIONS_IN_USE][0])
        if active_drive==None:
            active_drive=cur_active_drive
        elif active_drive != cur_active_drive:
            write_msg("Stopping: Degraded arrays running on multiple physical drives.")
            return 30

    # ok, one drive, all on same drive, it is stored in variable 'active_drive'
    active_device='/dev/'+active_drive
    target_drive=target_device=None
    
    # we _assume_ that we are a two disk system, so we look for a valid drive
    # where mdadm.conf expects it, we just have to look at an array entry
    # and pick the drive that _isn't_ currently in use
    for dev in arrays_hash[arrays_hash.keys()[0]][PARTITIONS_IN_CONF]:
        if not dev.startswith(active_drive):
            target_drive = strip_partition(dev)
            break
    
    if target_drive == None:
        write_msg("Stopping: Could not find second device for mirror in mdadm.conf.")
        return 40
        
    target_device='/dev/'+target_drive
    write_msg("Found potential target drive: "+target_drive)
    
    # now see if we have the drive and if it matches our criteria
    active_drive_size=disk_size_mb(active_drive)
    target_drive_size=disk_size_mb(target_drive)
    if active_drive_size==0 or target_drive_size==0:
        write_msg('Stopping: Cannot size drives. Cannot continue')
        return 50
    
    if not ( \
        is_scsi(target_drive) and \
        target_drive_size>=active_drive_size and \
        not drive_in_use(target_drive) \
        ): 
        write_msg("Stopping: Drive '"+target_drive+"' not found or not usable")
        return 60

    write_msg("Will attempt to add '"+target_drive+"' to mirror")
    # first trash any superblocks that might confuse mdadm
    with open(PARTITIONS) as f:
        for l in f:
            dev=l.split()
            if len(dev)==4 and \
                dev[3].startswith(target_drive) and \
                int(dev[1]) % 16 != 0:
                write_msg("Zeroing any superblock on: "+dev[3])
                sp.call(['mdadm','--zero-superblock','/dev/'+dev[3]])
                
    # now the MBR
    
    write_msg("Copying MBR and GRUB from '"+active_device+"' to '"+target_device+"'")
    sp.call(['dd','if='+active_device,'of='+target_device,'bs=512','count=64'])
   
    # GRUB install doesn't work unless system is _already_ synced and 
    # grub stage1.5 and stage2 are present in the file system...

    '''
    write_msg("Installing GRUB on new drive %s" % target_device)
    command = [GRUB, '--batch']
    child = sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT)
    child.stdin.write("device (hd0) %s\n" % target_device)
    child.stdin.write("root (hd0,0)\n")
    child.stdin.write("setup (hd0)\n")
    child.stdin.write("quit\n")
    child.communicate()
    '''

    # now copy over the partition table from the good drive
    write_msg("Copying partition table to: "+target_device)
    dump = sp.Popen(['sfdisk','-d',active_device], stdout=sp.PIPE)
    sp.Popen(['sfdisk', target_device], stdin=dump.stdout, stdout=sp.PIPE).communicate()
    
    # verify tables are now the same
    write_msg("Verifying partition table copied properly...")
    if not part_tables_same(active_device,target_device):
        write_msg("Oops. Just wrote partition table on '"+target_device+\
        "' and it doesn't match original table so I can't use the drive")
        return 70
    else:
        write_msg("Ok")
        
    # now add the drives to the array
    for key in arrays_hash.keys():
        array=arrays_hash[key]
        for part in array[PARTITIONS_IN_CONF]:
            if not part.startswith(active_drive):
                write_msg("Adding '"+part+"' to array '"+key+"'")
                sp.call(['mdadm',key,'--add','/dev/'+part])
                break

    write_msg("New device added to array. Please allow resync to finish before rebooting!")
    return 0

def re_add_partitions(arrays_hash):
    for key in arrays_hash.keys():
        array=arrays_hash[key]
        if not array[DEGRADED]: continue

        # find partitions(s) to re-add
        to_re_add=[]
        for conf_part in array[PARTITIONS_IN_CONF]:
            found_in_use=False
            for in_use_part in array[PARTITIONS_IN_USE]:
                if in_use_part == conf_part:
                    found_in_use=True
                    break
            if not found_in_use: to_re_add.append(conf_part)

        if len(to_re_add)==0:
            write_msg("%s is degraded but all drives are in use. Perhaps it is rebuilding itself." % key)
            continue
        
        # now try to re-add
        for part in to_re_add:
            write_msg("Attempt to re-add %s to array %s" % (part,key))
            if sp.call(['mdadm',key,'--add','/dev/'+part])==0:
                write_msg("Success")
            else:
                write_msg("Failed to add '%s' to array '%s'" % (part,key))
        # end inner for
    #end outer for
    return 0

def main():
    syslog.openlog('inv-rebuild-mirror', 0, syslog.LOG_LOCAL5)
    
    write_msg('Starting check of RAID1 mirror devices')
    
    # if not a raided root device, return
    if not is_root_device_raid(): 
        write_msg("Nothing to do: Root device is not a RAID array.")
        return 0

    # parse mdadm.conf
    arrays=parse_mdadm_conf(MDADM_CONF)
    if len(arrays) == 0: 
        write_msg("Nothing to do: No arrays found in "+MDADM_CONF)
        return 0
    
    # Gather info about state of the arrays
    all_degraded=True # assume degraded unless otherwise
    some_degraded=False # again, assume opposite
    for array in arrays.keys():
	array_hash=arrays[array]
	mdadm_proc=sp.Popen(['mdadm','-D','--test',array],stdout=sp.PIPE)
	mdadm_out=mdadm_proc.communicate()[0]

	array_hash[DEGRADED]=mdadm_proc.returncode != 0
        
	# set all_ and some_ degraded for later use
	all_degraded=all_degraded and array_hash[DEGRADED]
        some_degraded=some_degraded or array_hash[DEGRADED]

        # check the drives
        array_hash[PARTITIONS_IN_USE]=map(device_to_part, mdadm_detail_drive_matcher.findall(mdadm_out))


    # if ALL arrays degraded, try to find a spare drive and reformat and add to mirror
    if all_degraded:
        write_msg("All arrays degraded. Will look for spare drive to add to array")
        return add_drive_to_mirror(arrays)

    if some_degraded:
        write_msg("Some, but not all arrays degraded, will try to re-add missing parititons")
        return re_add_partitions(arrays)
    else:
        write_msg("No degraded arrays")
        return 0

    
if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/opt/inveneo/bin:/opt/inveneo/sbin'
    sys.exit(main())
