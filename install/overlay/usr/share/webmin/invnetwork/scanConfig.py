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

sys.path.append('/opt/inveneo/lib/python/inveneo')
import configfiles

CHKCONFIG = '/usr/sbin/sysv-rc-conf'
DHCPD = 'dhcp3-server'

# values for potential display on the webpage form
formvals = {}

# collect the interfaces
o = configfiles.EtcNetworkInterfaces()
wan = o.ifaces['eth0']
lan = o.ifaces['eth1']
ppp = o.ifaces['ppp0']

if wan:
    formvals['wan_interface'] = 'ethernet'
    if wan.method:  formvals['wan_method']  = wan.method
    if wan.address: formvals['wan_address'] = wan.address.strNormal()
    if wan.netmask: formvals['wan_netmask'] = wan.netmask.strNormal()
    if wan.gateway: formvals['wan_gateway'] = wan.gateway.strNormal()
else:
    formvals['wan_interface'] = 'off'

if lan:
    if lan.address: formvals['lan_address'] = lan.address.strNormal()
    if lan.netmask: formvals['lan_netmask'] = lan.netmask.strNormal()
    if lan.gateway: formvals['lan_gateway'] = lan.gateway.strNormal()

if 'ppp0' in o.autoset:
    formvals['wan_interface'] = 'modem'

# collect the modem definitions
o = configfiles.EtcWvdialConf()
for key, value in o.metadata.iteritems():
    formvals['ppp_%s' % key.replace(' ', '_')] = value

# scan the DHCP daemon config
o = configfiles.EtcDhcp3DhcpConf()
for subnet, sobj in o.subnets.iteritems():
    ipnm = IP('%s/%s' % (subnet, sobj.netmask.strNormal()))
    if lan.address and (lan.address in ipnm):
        if sobj.start_ip:
            s_start_ip = sobj.start_ip.strNormal()
        else:
            s_start_ip = 100
        if sobj.end_ip:
            s_end_ip = sobj.end_ip.strNormal()
        else:
            s_end_ip = 200
        formvals['lan_dhcp_range_start'] = s_start_ip.split('.')[3]
        formvals['lan_dhcp_range_end']   = s_end_ip.split('.')[3]

# scan the running daemons for DHCP
# XXX shouldn't this actually look for an existing startup script instead?
command = [CHKCONFIG, '--list', DHCPD]
output = Popen(command, stdout=PIPE).communicate()[0]
tokens = output.split()
level2 = tokens[2]
formvals['lan_dhcp_on'] = level2.split(':')[1]

# report the findings
#sys.stdout.write(urlencode(formvals))
s = ''
for key, value in formvals.iteritems():
    if value:
        s += '%s%s=%s' % (['','&'][len(s) > 0], quote(key), quote(value))
print s

