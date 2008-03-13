#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import subprocess as sp
sys.path.append('/opt/inveneo/lib/python')

SERIAL_MATCHER=re.compile(r'Serial:\s*(\S+)')

def id_for_device(dev):
    """
    returns the drive ID or 'None' if not available
    for a device in the form '/dev/sda'
    """

    output = sp.Popen(['hdparm','-I',dev], stdout=sp.PIPE).communicate()[0]
    m=SERIAL_MATCHER.search(output)

    if m:
        return m.groups(0)

    return None

if __name__ == '__main__':
    sys.exit(0)
