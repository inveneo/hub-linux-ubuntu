#!/usr/bin/env python

import os
import time
import sys
import syslog
import constants
import notify_icip
import get_disk_status
import update_disk_status

def main(disk=None):

        syslog.openlog('inv-degrade-actions', 0, syslog.LOG_LOCAL5)

	while True:

		# check if the array is restored
		old_disks = get_disk_status.main()
		new_disks = update_disk_status.main()
		if (new_disks >= old_disks):
                        syslog.syslog("Array appears to be restoring. Exiting.")
			return

                syslog.syslog("Performing actions")

		# INSERT YOUR ACTIONS BELOW

		os.system(constants.INV_MONITOR_BEEP_ALERT)
		notify_icip.send_notice()
		
		# INSERT YOUR ACTIONS ABOVE

                syslog.syslog("Sleeping")
		# sleep for some minutes
		time.sleep(constants.INV_MONITOR_DEGRADE_ACTIONS_SLEEP_MINUTES*60)

	# end while


if __name__ == '__main__':
	if len(sys.argv) == 1:
		main()
	sys.exit()
