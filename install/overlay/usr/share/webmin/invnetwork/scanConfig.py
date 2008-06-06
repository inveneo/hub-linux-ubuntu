#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scanConfig.py - scan some config files and return interesting values in
                a URL-encoded string

Copyright (c) 2007 Inveneo, inc. All rights reserved.
"""
# external modules
import sys, os, traceback
from IPy import IP
from urllib import quote
from inveneo import configfiles, processes

def appendQueryString(qs, key, value):
    """Helper for building up properly quoted query string."""
    sep = ['','&'][len(qs) > 0]
    return qs + '%s%s=%s' % (sep, quote(key), quote(value))

# values for potential display on the webpage form
formvals = {}

# collect the interfaces
o = configfiles.EtcNetworkInterfaces()
wan = o.ifaces.get('eth0', None)
lan = o.ifaces.get('eth1', None)
ppp = o.ifaces.get('ppp0', None)

if 'eth0' in o.autoset:
    formvals['wan_interface'] = 'eth0'
elif 'ppp0' in o.autoset:
    formvals['wan_interface'] = 'modem'
else:
    formvals['wan_interface'] = 'eth1'

formvals['wan_method'] = 'dhcp' # default
if wan:
    if wan.method:  formvals['wan_method']  = wan.method
    if wan.address: formvals['wan_address'] = wan.address.strNormal()
    if wan.netmask: formvals['wan_netmask'] = wan.netmask.strNormal()
    if wan.gateway: formvals['wan_gateway'] = wan.gateway.strNormal()

formvals['lan_address'] = '192.168.100.1' # default
if lan:
    # LAN is always static, and only has gateway if used as WAN access
    if lan.address: formvals['lan_address'] = lan.address.strNormal()
    if lan.netmask: formvals['lan_netmask'] = lan.netmask.strNormal()
    if lan.gateway: formvals['lan_gateway'] = lan.gateway.strNormal()

# collect the DNS servers
# XXX need to collect from dhclient.conf also
o = configfiles.EtcResolvConf()
formvals['dns_servers'] = ''
sep = ''
for value in o.nameservers:
    formvals['dns_servers'] += '%s%s' % (sep, value)
    sep = ' '

# collect the modem definitions
o = configfiles.EtcWvdialConf()
for key, value in o.metadata.iteritems():
    formvals['ppp_%s' % key.replace(' ', '_')] = value

# scan the DHCP daemon config
formvals['lan_dhcp_range_start'] = '100' # default
formvals['lan_dhcp_range_end']   = '200' # default
o = configfiles.EtcDhcp3DhcpConf()
if lan and lan.address:
    for subnet, sobj in o.subnets.iteritems():
        if not sobj.netmask: continue
        ipnm = IP('%s/%s' % (subnet, sobj.netmask.strNormal()))
        if lan.address in ipnm:
            if sobj.start_ip:
                s_start_ip = sobj.start_ip.strNormal()
                formvals['lan_dhcp_range_start'] = s_start_ip.split('.')[3]
            if sobj.end_ip:
                s_end_ip = sobj.end_ip.strNormal()
                formvals['lan_dhcp_range_end']   = s_end_ip.split('.')[3]

# grab the hostname
o = configfiles.EtcHostname()
formvals['hostname'] = o.hostname

# get list of currently executing processes
procs = processes.ProcSnap()
formvals['lan_dhcp_on'] = ['off', 'on'][procs.is_running('/usr/sbin/dhcpd3')]

# report the findings
#sys.stdout.write(urlencode(formvals))
qs = ''
for key, value in formvals.iteritems():
    if value:
        qs = appendQueryString(qs, key, value)
print qs

