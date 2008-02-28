#!/usr/bin/env python

from __future__ import with_statement

import os

# Needs to run as root or sudo

DISK_STATUS_FILE='/etc/inveneo/disk_status_count'

if not os.path.exists(DISK_STATUS_FILE):
    os.system('/opt/inveneo/lib/python/inveneo/update_disk_status.py')

with open(DISK_STATUS_FILE) as f:
    print f.read()
