#!/usr/bin/env python

import notify_icip
import os
import time
import sys
import constants

def main(disk=None):
	while True:
		os.system(constants.INV_MONITOR_BEEP_ALERT)
		notify_icip.send_notice()
		time.sleep(constants.INV_MONITOR_DEGRADE_ACTIONS_SLEEP_MINUTES*60)


if __name__ == '__main__':
	if len(sys.argv) == 1:
		main()
	sys.exit()
