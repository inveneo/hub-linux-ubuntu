#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import syslog
import socket
import smtplib
import os
from os import path
import StringIO
import subprocess as sp
sys.path.append('/opt/inveneo/lib/python')
import constants
import fileutils

ACTIVE_DEV_MATCHER=re.compile(r'Active Devices\s+:\s+(\d)')
WORKING_DEV_MATCHER=re.compile(r'Working Devices\s+:\s+(\d)')
MDADM_START_MATCHER=re.compile(r'^\s*Number\s+Major')

def num_working_drives_in_array(array_dev='/dev/md0'):
    """
    Includes functioning drives that are not fully synched
    """
    
    return num_drives_in_array(WORKING_DEV_MATCHER, array_dev)

def num_active_drives_in_array(array_dev='/dev/md0'):
    """
    Only drives actively synched and in use in the array
    """
    
    return num_drives_in_array(ACTIVE_DEV_MATCHER, array_dev)
    
def num_drives_in_array(matcher, array_dev):
    output = sp.Popen(['mdadm','--detail',array_dev], stdout=sp.PIPE).communicate()[0]
    
    m=matcher.search(output)

    if not m:
        raise Exception("Could not find number of working drives for device: %s, are you root?" % array_dev)

    return int(m.groups()[0])

def get_missing_drives_for_array(array_dev='/dev/md0'):
    """
    returns list of tuples ((hw logical name, serial num),(...,...)) for
    any missing drives.

    Or None.

    Usually 'None' if everything is good OR a single drive since
    we only support mirroring right now.

    E.g. ((1,'SDJ72346'))
    """

    

def sound_audio_notice(config):
    success=True
    try:
        sp.call(config.get_as_str('BEEP_CMD').split())
    except:
        success=False

    return success
  
def drives_in_array(array_dev='/dev/md0'):
    """returns drive in an array and status None.
    Input arg is of form "md0" "/dev/md0"
    Output is of form "[(sda1,'active'),(sdb2,'faulty')]"

    Guaranteed to be returned in proper order (e.g. sda before sdb)

    states are: active, fauly, spare (probably being rebuilt)
    """

    # make sure whatever the input, md0 or /dev/md0 we get the right arg for mdadm
    array_dev='/dev/'+array_dev.split('/')[-1]

    output = StringIO.StringIO(sp.Popen(['mdadm','--detail',array_dev], stdout=sp.PIPE).communicate()[0])
    devices=[]
    start_caring=False
    for line in output:
        if not start_caring:
            if MDADM_START_MATCHER.match(line):
                start_caring=True
        else:
            devinfo=line.strip().split()[4:]
            if len(devinfo)>=3:
                devices.append((devinfo[-1].split('/')[-1],devinfo[0]))

    if len(devices)==0:
        return None
    else:
        devices.sort(lambda x,y: cmp(x[0],y[0]))

    return devices
                
            
    
    
def send_email_notice(config, subject='', message=''):
    syslog.openlog('raidutils send_email_notice', 0, syslog.LOG_LOCAL5)

    # take care of defaults
    if subject == '':
        subject=config.get_as_str('MONITOR_SMTP_DEFAULT_SUBJECT')

    if message == '':
        message=config.get_as_str('MONITOR_SMTP_DEFAULT_MESSAGE') + " " + socket.gethostname()
    
    if config.get_as_str('MONITOR_SMTP_RECIPIENT') == '':
        syslog.syslog("Recipient email not set. Not sending email.")
        print 'unable to send message, please set recipient email'
        return False
        
    message = subject + "\n\n" + message
    try:
        syslog.syslog("Opening SMTP connection")
        s = smtplib.SMTP(config.get_as_str('MONITOR_SMTP_HOSTNAME'), config.get_as_int('MONITOR_SMTP_PORT',25))
        # s.set_debuglevel(1)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(config.get_as_str('MONITOR_SMTP_USERNAME'), config.get_as_str('MONITOR_SMTP_PASSWORD'))
        s.sendmail(config.get_as_str('MONITOR_SMTP_SENDER'), config.get_as_str('MONITOR_SMTP_RECIPIENT'), message)
        s.noop()
        s.rset()
        s.quit()
        s.close()
        syslog.syslog("Closed SMTP connection")
    except Exception, e:
        syslog.syslog("Unable to send message. Exception: " + e.message)
        return False

    return True


if __name__ == '__main__':
    print "drives in md0: "+str(drives_in_array('/dev/md0'))

