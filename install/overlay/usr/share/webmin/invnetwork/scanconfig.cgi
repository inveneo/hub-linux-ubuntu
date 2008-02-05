#!/usr/bin/env python

import os
from subprocess import Popen, PIPE
from urllib import urlencode, quote

IFCONF = '/etc/network/interfaces'
WVCONF = '/etc/wvdial.conf'
DHCPD = 'dhcp3-server'
CHKCONFIG = '/usr/sbin/sysv-rc-conf'
DHCPCONF = '/etc/dhcp3/dhcpd.conf'

autos = set()
values = {}
iface = None

# scan the interfaces
fin = open(IFCONF, 'r')
for line in fin.readlines():
    tokens = line.strip().split()
    if tokens:
        if tokens[0] == 'auto':
            autos.update(tokens[1:])
        elif tokens[0] == 'iface':
            iface = tokens[1]
            method = tokens[3]
            if iface == 'eth0':
                values['wan_type'] = method
        elif tokens[0] == 'address':
            if iface == 'eth0':
                values['wan_address'] = tokens[1]
            elif iface == 'eth1':
                values['lan_address'] = tokens[1]
        elif tokens[0] == 'netmask':
            if iface == 'eth0':
                values['wan_netmask'] = tokens[1]
            elif iface == 'eth1':
                values['lan_netmask'] = tokens[1]
        elif tokens[0] == 'gateway':
            if iface == 'eth0':
                values['wan_gateway'] = tokens[1]

if 'ppp0' in autos:
    values['wan_type'] = 'modem'

fin.close()

# scan the modem definitions
if os.path.exists(WVCONF):
    fin = open(WVCONF, 'r')
    for line in fin.readlines():
        eq = line.find('=')
        if eq > 0:
            key = line[0:eq].strip().lower()
            value = line[eq+1:].strip()
            if key == 'phone':
                values['ppp_phone'] = value
            elif key == 'username':
                values['ppp_username'] = value
            elif key == 'password':
                values['ppp_password'] = value
            elif key == 'baud':
                values['ppp_baud'] = value
            elif key == 'idle seconds':
                values['ppp_idle_seconds'] = value
            elif key == 'init1':
                values['ppp_init1'] = value
            elif key == 'init2':
                values['ppp_init2'] = value
    fin.close()

# scan the running daemons for DHCP
command = [CHKCONFIG, '--list', DHCPD]
output = Popen(command, stdout=PIPE).communicate()[0]
tokens = output.split()
result = tokens[2]
values['lan_dhcp_on'] = result.split(':')[1]

# scan the DHCP daemon config
fin = open(DHCPCONF, 'r')
for line in fin.readlines():
    tokens = line.strip().split()
    if tokens:
        if tokens[0] == 'range':
            start_ip = tokens[1]
            end_ip = tokens[2].strip(';')
            values['lan_dhcp_range_start'] = start_ip.split('.')[3]
            values['lan_dhcp_range_end'] = end_ip.split('.')[3]
        pass
fin.close()

# report the findings
#print urlencode(values)
s = ''
for key, value in values.iteritems():
    s += '%s%s=%s' % (['','&'][len(s) > 0], quote(key), quote(value))
print s

