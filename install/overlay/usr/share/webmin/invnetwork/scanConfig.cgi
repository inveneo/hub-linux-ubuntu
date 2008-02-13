#!/usr/bin/env python

import os, sys, traceback
from subprocess import Popen, PIPE
from urllib import urlencode, quote
from IPy import IP
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
        metadata['wan_type']    = wan.get('method', None)
        metadata['wan_address'] = wan.get('address', None)
        metadata['wan_netmask'] = wan.get('netmask', None)
        metadata['wan_gateway'] = wan.get('gateway', None)

    if lan:
        metadata['lan_address'] = lan.get('address', None)
        metadata['lan_netmask'] = lan.get('netmask', None)

    if 'ppp0' in o.autoset:
        metadata['wan_type'] = 'modem'

    # collect the modem definitions
    o = netfiles.EtcWvdialConf()
    for key, value in o.metadata.iteritems():
        metadata['ppp_%s' % key.replace(' ', '_')] = value

    # scan the DHCP daemon config
    o = netfiles.EtcDhcp3DhcpConf()
    for network, params in o.subnets.iteritems():
        subnet = IP('%s/%s' % (network, params['netmask']))
        if metadata['lan_address'] in subnet:
            start_ip = params.get('start_ip', None)
            end_ip = params.get('end_ip', None)
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
    #print urlencode(metadata)
    s = ''
    for key, value in metadata.iteritems():
        if value:
            s += '%s%s=%s' % (['','&'][len(s) > 0], quote(key), quote(value))
    print s

if __name__ == '__main__':
    main()
