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

formvals = {}

def main():

    # collect the interfaces
    o = netfiles.EtcNetworkInterfaces()
    wan = o.ifaces['eth0']
    lan = o.ifaces['eth1']
    ppp = o.ifaces['ppp0']

    if wan:
        formvals['wan_interface'] = 'ethernet'
        formvals['wan_method']  = wan.method
        formvals['wan_address'] = wan.address
        formvals['wan_netmask'] = wan.netmask
        formvals['wan_gateway'] = wan.gateway
    else:
        formvals['wan_interface'] = 'off'

    if lan:
        formvals['lan_address'] = lan.address
        formvals['lan_netmask'] = lan.netmask
        formvals['lan_gateway'] = lan.gateway

    if 'ppp0' in o.autoset:
        formvals['wan_interface'] = 'modem'

    # collect the modem definitions
    o = netfiles.EtcWvdialConf()
    for key, value in o.metadata.iteritems():
        formvals['ppp_%s' % key.replace(' ', '_')] = value

    # scan the DHCP daemon config
    o = netfiles.EtcDhcp3DhcpConf()
    for subnet, sobj in o.subnets.iteritems():
        ipnm = IP('%s/%s' % (subnet, sobj.netmask))
        if formvals['lan_address'] in ipnm:
            start_ip = sobj.start_ip
            end_ip = sobj.end_ip
            formvals['lan_dhcp_range_start'] = start_ip.split('.')[3]
            formvals['lan_dhcp_range_end']   = end_ip.split('.')[3]

    # scan the running daemons for DHCP
    # XXX shouldn't this actually look for an existing startup script instead?
    command = [CHKCONFIG, '--list', DHCPD]
    output = Popen(command, stdout=PIPE).communicate()[0]
    tokens = output.split()
    result = tokens[2]
    formvals['lan_dhcp_on'] = result.split(':')[1]

    # report the findings
    sys.stdout.write(urlencode(formvals))
    """
    s = ''
    for key, value in formvals.iteritems():
        if value:
            s += '%s%s=%s' % (['','&'][len(s) > 0], quote(key), quote(value))
    print s
    """

if __name__ == '__main__':
    main()

