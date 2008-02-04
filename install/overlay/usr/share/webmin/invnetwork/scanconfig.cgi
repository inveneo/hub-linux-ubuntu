#!/usr/bin/env python

CONFIG = '/etc/network/interfaces'

autos = set()
values = {}
iface = None

fin = open(CONFIG, 'r')
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
    values['wan_type'] = 'dialup'

fin.close()

s = ''
for key, val in values.iteritems():
    s += '%s%s=%s' % (['',','][len(s) > 0], key, val)
print s
