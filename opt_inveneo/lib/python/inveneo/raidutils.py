#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import syslog
import socket
import smtplib
import subprocess as sp
sys.path.append('/opt/inveneo/lib/python')
import constants
import fileutils

WORK_DEV_MATCHER=re.compile(r'Working Devices\s+:\s+(\d)')

def num_active_drives_in_array(array_dev):
    output = sp.Popen(['mdadm','--detail',array_dev], stdout=sp.PIPE).communicate()[0]
    
    m=WORK_DEV_MATCHER.search(output)

    if not m:
        raise Exception("Could not find number of working drives for device: %s, are you root?" % array_dev)

    return int(m.groups()[0])

def sound_audio_notice(config):
    success=True
    try:
        sp.call(config.dict['BEEP_CMD'].split())
    except:
        success=False

    return success
  

def send_email_notice(config, subject='', message=''):
    syslog.openlog('raidutils send_email_notice', 0, syslog.LOG_LOCAL5)

    # take care of defaults
    if subject == '':
        subject=config.dict['MONITOR_SMTP_DEFAULT_SUBJECT']

    if message == '':
        message=config.dict['MONITOR_SMTP_DEFAULT_MESSAGE'] + " " + socket.gethostname()
    
    if config.dict['MONITOR_SMTP_RECIPIENT'] == '':
        syslog.syslog("Recipient email not set. Exiting.")
        print 'unable to send message, please set recipient email'
        return False
        
    message = subject + "\n\n" + message
    try:
        syslog.syslog("Opening SMTP connection")
        s = smtplib.SMTP(config.dict['MONITOR_SMTP_HOSTNAME'], int(config.dict['MONITOR_SMTP_PORT']))
        # s.set_debuglevel(1)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(config.dict['MONITOR_SMTP_USERNAME'], config.dict['MONITOR_SMTP_PASSWORD'])
        s.sendmail(config.dict['MONITOR_SMTP_SENDER'], config.dict['MONITOR_SMTP_RECIPIENT'], message)
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
    print "Num active drives in md0: "+str(num_active_drives_in_array('/dev/md0'))
    config = fileutils.ConfigFileDict(constants.INV_RAID_MONITOR_CONFIG_FILE)
    sound_audio_notice(config)
