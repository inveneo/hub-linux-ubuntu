#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import re

# Needs to run as root or sudo

# Also needs to be idempotent, meaning you can run it multiple times and it will do the same thing each time

DISK_STATUS_FILE='/etc/inveneo/disk_status_count'

def main():
    earlier_disks = -1

    if os.path.exists(DISK_STATUS_FILE):
        with open(DISK_STATUS_FILE) as f:
            earlier_disks = int(f.read())

    output = ''
    try:
        mdadm_command = os.popen('mdadm --detail /dev/md0')
        output = mdadm_command.read()
    finally:
        try:
            mdadm_command.close()
        except:
            pass

    find_working = re.compile(r'Working Devices\s+:\s+(\d)')
    result = find_working.findall(output)

    detected_disks = -1

    if result:
        detected_disks = int(result[0])

    if (earlier_disks < detected_disks):
        with open(DISK_STATUS_FILE, 'w') as f:
            print >>f, detected_disks

    return detected_disks

if __name__ == '__main__':
	number_of_disks = main()
	sys.exit()
