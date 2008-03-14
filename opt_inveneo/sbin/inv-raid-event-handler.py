#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import syslog
import subprocess as sp
sys.path.append('/opt/inveneo/lib/python')
from inveneo import constants, fileutils, raidutils, pidfile
from time import sleep

class RaidEventHandler:
    def __init__(self):
        pass
    
    def main(self, event, device):
        syslog.openlog('raid-status-monitor', 0, syslog.LOG_LOCAL5)
        syslog.syslog("Received RAID event: %s for device: %s" % (event,device))
        
        # is this an error event?
        errorEvent=False
        if event == "Fail" or event == "DegradedArray" or event == "FailSpare" or event == "SpareMissing":
            errorEvent=True
        
        if not errorEvent:
            syslog.syslog("Event: %s not considered on error." % event)
            
        # but continue to drive number check in case we want to upgrade expectations
        
        config = fileutils.ConfigFileDict(constants.INV_RAID_MONITOR_CONFIG_FILE)
        expected_drives=config.get_as_int('MONITOR_EXPECTED_NUM_DRIVES',1)
        
        current_drives = raidutils.num_working_drives_in_array(device)
        
        # first see if the number of drives we have is _greater_ than the expected number
        # of drives. If so, we have moved from 1 drive to 2 drive system and need to update
        # our expectations, but no need to make any notifications.
        
        if current_drives > expected_drives:
            syslog.syslog("Upgrading RAID expectations: Expected %d active drives in array and found %d" % \
                          (expected_drives, current_drives))
            
            config.set_as_str('MONITOR_EXPECTED_NUM_DRIVES',current_drives)
            config.save_config()
            
            sp.call(['/opt/inveneo/sbin/inv-id-md-drives.py',device])
            # TO DO: Notify that new drive has appeared?
            return 0
        
        # Now see if the are equivalent, and just exit
        if current_drives == expected_drives:
            syslog.syslog("Found expected number of drives. Exiting")
            return 0
        
        # so now we know we have _fewer_ drives than expected, but this is not necessarily an errror event we are processing
        if not errorEvent:
            syslog.syslog("Not processing error event.")
            return 0
        
        # Ok, so now we know we have an error state, but we don't want to notify if a notifying process
        # is already running
        # do this in a while loop so that we keep trying to grab the file until either we own it
        # or some other _running_ process does
        
        p=pidfile.PIDFile(constants.INV_RAID_MONITOR_PID_FILE_NAME)
        while not p.pid_is_this_process():
            if p.is_running():
                # someone else is already running
                syslog.syslog("Failure event, but notifier process already running")
                return 0
            else:
                p.remove_pid_file()
                p=pidfile.PIDFile(constants.INV_RAID_MONITOR_PID_FILE_NAME)
        
        
        # Now for the actual notifications. This will be a check status->notify->sleep loop.
        
        # 1. check that things haven't improved, we can do this in while condition
        sleep_interval=10
        sleep_count=0
        email_interval=config.get_as_int('EMAIL_INTERVAL',1440)
        email_last_fail=False
        beep_interval=config.get_as_int('BEEP_INTERVAL',60)
        beep_last_fail=False
        
        # start out with a sleep to avoid the warning on first boot
        # with a new drive (degrade will be reported before we are
        # notified of the new drive)
        syslog.syslog("Waiting briefly before starting alerts.")
        sleep(3*60)
        current_drives = raidutils.num_working_drives_in_array(device)
        while current_drives < expected_drives:
            if email_last_fail or ((sleep_count * sleep_interval) % email_interval) < sleep_interval:
                email_last_fail = not raidutils.send_email_notice(config)
            
            if beep_last_fail or ((sleep_count * sleep_interval) % beep_interval) < sleep_interval:
                beep_last_fail = not raidutils.sound_audio_notice(config)
            
            sleep(sleep_interval * 60)
            sleep_count+=1
            current_drives = raidutils.num_working_drives_in_array(device)
        
        syslog.syslog("While waiting to alert, found expected number of drives. Array is reconstructed.")
        # TO DO: Send array fixed email?
        return 0

if __name__ == '__main__':
    syslog.openlog('raid-status-monitor', 0, syslog.LOG_LOCAL5)
    if len(sys.argv) not in (3,4):
        sys.stderr.write("Usage: raid-status-handler <status> <device> [<related-device>]\n")
        syslog.syslog("received bad args: %s" % str(sys.argv[1:]))
        sys.exit(1)
    
    sys.exit(RaidEventHandler().main(sys.argv[1], sys.argv[2]))
