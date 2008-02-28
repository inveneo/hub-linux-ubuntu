import notify_icip
import os
import time
import sys

BEEP_ALERT='beep -f 1000 -n -f 1200 -n -f 1500 -n -f 1700 -n -f 1950 -n -f 2200 -n -f 2400 -n -f 2700'
DEGRADE_ACTIONS_SLEEP_MINUTES=30


def main(disk=None):
	while True:
		os.system(BEEP_ALERT)
		notify_icip.send_notice()
		time.sleep(DEGRADE_ACTIONS_SLEEP_MINUTES*60)


if __name__ == '__main__':
	if len(sys.argv) == 1:
		main()
	sys.exit()
