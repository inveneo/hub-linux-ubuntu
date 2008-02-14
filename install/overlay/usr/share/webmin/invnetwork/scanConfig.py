#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scanConfig.py - scan some config files and return interesting values in
                a URL-encoded string

Copyright (c) 2007 Inveneo, inc. All rights reserved.
"""

import os, sys, traceback
from subprocess import Popen, PIPE
from urllib import urlencode, quote
from IPy import IP

sys.path.append('/opt/inveneo/lib/python')
import netfiles

CHKCONFIG = '/usr/sbin/sysv-rc-conf'
DHCPD = 'dhcp3-server'

metadata = {}

def main():

    # collect the interfaces
    o = netfiles.EtcNetworkInterfaces()
    wan = o.ifaces['eth0']
    lan = o.ifaces['eth1']
    ppp = o.ifaces['ppp0']

    if wan:
        metadata['wan_interface'] = 'eth0'
        metadata['wan_method']  = wan.get('method', None)
        metadata['wan_address'] = wan.get('address', None)
        metadata['wan_netmask'] = wan.get('netmask', None)
        metadata['wan_gateway'] = wan.get('gateway', None)
    else:
        metadata['wan_interface'] = 'off'

    if lan:
        metadata['lan_address'] = lan.get('address', None)
        metadata['lan_netmask'] = lan.get('netmask', None)
        metadata['lan_gateway'] = lan.get('gateway', None)

    if 'ppp0' in o.autoset:
        metadata['wan_interface'] = 'modem'

    # collect the modem definitions
    o = netfiles.EtcWvdialConf()
    for key, value in o.metadata.iteritems():
        metadata['ppp_%s' % key.replace(' ', '_')] = value

    # scan the DHCP daemon config
    o = netfiles.EtcDhcp3DhcpConf()
    for subnet, sobj in o.subnets.iteritems():
        ipnm = IP('%s/%s' % (subnet, sobj.netmask))
        if metadata['lan_address'] in ipnm:
            start_ip = sobj.start_ip
            end_ip = sobj.end_ip
            metadata['lan_dhcp_range_start'] = start_ip.split('.')[3]
            metadata['lan_dhcp_range_end']   = end_ip.split('.')[3]

    # scan the running daemons for DHCP
    # XXX shouldn't this actually look for an existing startup script instead?
    command = [CHKCONFIG, '--list', DHCPD]
    output = Popen(command, stdout=PIPE).communicate()[0]
    tokens = output.split()
    result = tokens[2]
    metadata['lan_dhcp_on'] = result.split(':')[1]

    # report the findings
    sys.stdout.write(urlencode(metadata))
    """
    s = ''
    for key, value in metadata.iteritems():
        if value:
            s += '%s%s=%s' % (['','&'][len(s) > 0], quote(key), quote(value))
    print s
    """

if __name__ == '__main__':
    main()

