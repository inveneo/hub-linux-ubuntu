#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import with_statement

import os
import sys
import syslog
import traceback
from os import stderr,stdout

PROC_PATH="/sys/class/net"
MAC_FILE="address"
WAN="eth0"
LAN="eth1"

HEADER="""# This file assignes persistant names to network interfaces
# See iftab(5) for more information
# This file was generated by Invneo's Hub Station install script

"""


def main():
    syslog.openlog('geniftab', 0, syslog.LOG_LOCAL5)
    
    try:
        with open(PROC_PATH+"/"+WAN+"/"+MAC_FILE) as f:
            wan_mac=f.readline().strip()
        with open(PROC_PATH+"/"+LAN+"/"+MAC_FILE) as f:
            lan_mac=f.readline().strip()
    except Exception, ex:
        syslog.syslog("Cannot open mac address files in: "+PROC_PATH)
        traceback.print_exc(20,sys.stderr)
        return 1

    stdout.write(HEADER+"# "+WAN+"\n"+WAN+" mac "+wan_mac+" arp 1\n")
    stdout.write("# "+LAN+"\n"+LAN+" mac "+lan_mac+" arp 1\n")
    
    return 0
        
                
if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    sys.exit(main())
