#!/usr/bin/env python

from __future__ import with_statement

import os
import sys

# Needs to run as root or sudo

DISK_STATUS_FILE='/etc/inveneo/disk_status_count'

def main():
    if not os.path.exists(DISK_STATUS_FILE):
        os.system('/opt/inveneo/lib/python/inveneo/update_disk_status.py')

    with open(DISK_STATUS_FILE) as f:
        number_of_disks = int(f.read())
    
    return number_of_disks

if __name__ == '__main__':
	number_of_disks = main()
	print number_of_disks
	sys.exit()