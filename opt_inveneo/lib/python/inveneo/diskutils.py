#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import subprocess as sp

SERIAL_MATCHER=re.compile(r'Serial Number:\s*(\S+)')

def id_for_device(dev):
    """
    returns the drive ID or 'None' if not available
    for a device in the form '/dev/sda'
    """

    output = sp.Popen(['hdparm','-I',dev], stdout=sp.PIPE).communicate()[0]
    m=SERIAL_MATCHER.search(output)

    if m:
        return m.groups()[0]

    return None

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage diskutils.py <device>"
        sys.exit(-1)
        
    print id_for_device(sys.argv[1])
    sys.exit(0)
