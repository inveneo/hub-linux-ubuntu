#!/usr/bin/env python

import os
from subprocess import Popen, PIPE
from urllib import urlencode, quote

import netfiles

CHKCONFIG = '/usr/sbin/sysv-rc-conf'
DHCPD = 'dhcp3-server'

pairs = {}

# collect the interfaces
o = netfiles.EtcNetworkInterfaces()
wan = o.ifaces['eth0']
lan = o.ifaces['eth1']
ppp = o.ifaces['ppp0']

if wan:
    pairs['wan_type']    = wan.get('method', None)
    pairs['wan_address'] = wan.get('address', None)
    pairs['wan_netmask'] = wan.get('netmask', None)
    pairs['wan_gateway'] = wan.get('gateway', None)

if lan:
    pairs['lan_address'] = lan.get('address', None)
    pairs['lan_netmask'] = lan.get('netmask', None)

if 'ppp0' in o.autoset:
    pairs['wan_type'] = 'modem'

# collect the modem definitions
o = netfiles.EtcWvdialConf()
for key, value in o.pairs.iteritems():
    pairs['ppp_%s' % key.replace(' ', '_')] = value

# scan the DHCP daemon config
o = netfiles.EtcDhcp3DhcpConf()
pairs['lan_dhcp_range_start'] = o.pairs.get('dhcp_range_start', None)
pairs['lan_dhcp_range_end']   = o.pairs.get('dhcp_range_end', None) 

# scan the running daemons for DHCP
# XXX shouldn't this actually look for an existing startup script instead?
command = [CHKCONFIG, '--list', DHCPD]
output = Popen(command, stdout=PIPE).communicate()[0]
tokens = output.split()
result = tokens[2]
pairs['lan_dhcp_on'] = result.split(':')[1]

# report the findings
#print urlencode(pairs)
s = ''
for key, value in pairs.iteritems():
    if value:
        s += '%s%s=%s' % (['','&'][len(s) > 0], quote(key), quote(value))
print s

