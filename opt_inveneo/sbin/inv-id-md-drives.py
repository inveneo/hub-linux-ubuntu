#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import syslog
sys.path.append('/opt/inveneo/lib/python')
from inveneo import constants, raidutils, fileutils, diskutils
from time import sleep

class IdentifyMDDrives:
    def __init__(self):
	pass

    def	main(self, md):
	""" Identify the drives in the MD array be serial number 
	and record in raid_monitor.conf.

	Argument is of form 'md0'
        """
        
        syslog.openlog('inv-driveid', 0, syslog.LOG_LOCAL5)

	# drives come back sorted for me! Whee!
        drives=raidutils.drives_in_array(md)
        if drives == None:
            message="No drives found for device: %s\n" % md
            syslog.syslog(message)
            sys.stderr.write(message+"\n")
            return -1
        
        if len(drives) != 2:
            message="Only 1 drive found, not recording result"
            syslog.syslog(message)
            sys.stderr.write(message+"\n")
            return 0
            
        # load config
        config = fileutils.ConfigFileDict(constants.INV_RAID_MONITOR_CONFIG_FILE)

        for x in (0,1):
            id = diskutils.id_for_device('/dev/'+drives[x][0])
            disk='DISK'+str(x+1)
            config.set_as_str(disk,id)
            message="%s id: %s" % (disk, id)
            sys.stdout.write(message+"\n")
            syslog.syslog(message)

        config.save_config()
        
        return 0
                
if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: inv-id-md-drives.py <md device, e.g. /dev/md0>\n")
        sys.exit(1)
        
    sys.exit(IdentifyMDDrives().main(sys.argv[1].split('/')[-1]))
