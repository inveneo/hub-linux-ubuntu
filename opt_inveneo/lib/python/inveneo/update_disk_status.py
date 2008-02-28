#!/usr/bin/env python

from __future__ import with_statement

import os
import re

# Needs to run as root or sudo

# Also needs to be idempotent, meaning you can run it multiple times and it will do the same thing each time

DISK_STATUS_FILE='/etc/inveneo/disk_status_count'

earlier_disks = -1

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

if result:
    earlier_disks = int(result[0])

with open(DISK_STATUS_FILE, 'w') as f:
    print >>f, earlier_disks
