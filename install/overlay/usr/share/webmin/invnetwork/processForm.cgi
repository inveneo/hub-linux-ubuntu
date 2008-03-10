#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
processForm.cgi

Copyright (c) 2007 Inveneo, inc. All rights reserved.
"""

import os, sys, string
import cgi
import cgitb; cgitb.enable()  # XXX remove this for production systems
from IPy import IP

sys.path.append('/opt/inveneo/lib/python/inveneo')
import configfiles

ERR_PREFIX = 'err_'
errors = {}
form = cgi.FieldStorage()

# uncomment this section for some debugging
#print "Content-Type: text/html"
#print
#for key in form.keys():
#    print '%s = %s<br>' % (key, form[key].value)

# get submitted form values and validate them
wan_interface = form.getfirst("wan_interface", "").lower()
if not wan_interface in ['off', 'ethernet', 'modem']:
    errors['wan_interface'] = 'Invalid WAN interface'
wan_method = form.getfirst("wan_method", "").lower()
if not wan_method in ['off', 'dhcp', 'static']:
    errors['wan_method'] = 'Invalid WAN method'
wan_address = form.getfirst("wan_address", "").lower()
try:
    ip_wan_address = IP(wan_address)
except:
    errors['wan_address'] = 'Invalid IP address'
wan_netmask = form.getfirst("wan_netmask", "").lower()
try:
    ip_wan_netmask = IP(wan_netmask)
except:
    errors['wan_netmask'] = 'Invalid netmask'
wan_gateway = form.getfirst("wan_gateway", "").lower()
try:
    ip_wan_gateway = IP(wan_gateway)
except:
    errors['wan_gateway'] = 'Invalid gateway address'
dns_0 = form.getfirst("dns_0", None)
try:
    ip_dns_0 = IP(dns_0)
except:
    errors['dns_0'] = 'Invalid IP address'
dns_1 = form.getfirst("dns_1", None)
if dns_1:
    try:
        ip_dns_1 = IP(dns_1)
    except:
        errors['dns_1'] = 'Invalid IP address'

ppp_modem    = form.getfirst("ppp_modem", "/dev/modem")
ppp_phone    = form.getfirst("ppp_phone", "")
ppp_username = form.getfirst("ppp_username", "")
ppp_password = form.getfirst("ppp_password", "")
ppp_baud     = form.getfirst("ppp_baud", "9600")
try:
    int(ppp_baud)
except:
    errors['ppp_baud'] = 'Must be an integer'
ppp_idle_seconds = form.getfirst("ppp_idle_seconds", "60")
try:
    int(ppp_idle_seconds)
except:
    errors['ppp_idle_seconds'] = 'Must be an integer'
ppp_init1 = form.getfirst("ppp_init1", "ATZ")
ppp_init2 = form.getfirst("ppp_init2", "")

lan_address = form.getfirst("lan_address", "192.168.100.1").lower()
try:
    ip_lan_address = IP(lan_address)
except:
    errors['lan_address'] = 'Invalid IP address'
lan_netmask = form.getfirst("lan_netmask", "255.255.255.0").lower()
try:
    ip_lan_netmask = IP(lan_netmask)
except:
    errors['lan_netmask'] = 'Invalid netmask'
lan_gateway = form.getfirst("lan_gateway", "192.168.100.1").lower()
try:
    ip_lan_gateway = IP(lan_gateway)
except:
    errors['lan_gateway'] = 'Invalid gateway address'

bool_lan_dhcp_on = form.getfirst("lan_dhcp_on", "") != ""

lan_dhcp_range_start = form.getfirst("lan_dhcp_range_start", "100").lower()
try:
    int(lan_dhcp_range_start)
except:
    errors['lan_dhcp_range_start'] = 'Must be an integer'
lan_dhcp_range_end = form.getfirst("lan_dhcp_range_end", "200").lower()
try:
    int(lan_dhcp_range_end)
except:
    errors['lan_dhcp_range_end'] = 'Must be an integer'

# do higher level logic
try:
    ip_lan_network = IP(ip_lan_address.int() & ip_lan_netmask.int())
except:
    errors['lan_network'] = 'Invalid network'
try:
    ip_lan_network_range = IP('%s/%s' % (ip_lan_network, ip_lan_netmask))
except:
    errors['lan_network_range'] = 'Invalid network range'

# write /etc/resolv.conf if no errors
valset = set(['dns_0', 'dns_1'])
if len(valset.intersection(set(errors.keys()))) == 0:
    o = configfiles.EtcResolvConf()
    dns_0 = ip_dns_0.strNormal()
    if len(o.nameservers) > 0:
        o.nameservers[0] = dns_0
    else:
        o.nameservers.append(dns_0)
    if dns_1:
        dns_1 = ip_dns_1.strNormal()
        if len(o.nameservers) > 1:
            o.nameservers[1] = dns_1
        else:
            o.nameservers.append(dns_1)
    o.write()

# write /etc/wvdial.conf if no errors
valset = set(['ppp_modem', 'ppp_phone', 'ppp_username', 'ppp_password', \
        'ppp_baud', 'ppp_idle_seconds', 'ppp_init1', 'ppp_init2'])
if len(valset.intersection(set(errors.keys()))) == 0:
    o = configfiles.EtcWvdialConf()
    o.metadata['modem']        = ppp_modem
    o.metadata['phone']        = ppp_phone
    o.metadata['username']     = ppp_username
    o.metadata['password']     = ppp_password
    o.metadata['baud']         = ppp_baud
    o.metadata['idle seconds'] = ppp_idle_seconds
    o.metadata['init1']        = ppp_init1
    o.metadata['init2']        = ppp_init2
    o.write()

# write /etc/dhcp3/dhcp.conf if no errors
# XXX assumes subnets already exist: need method for creating them
valset = set(['lan_address', 'lan_netmask', 'lan_network', \
        'lan_dhcp_range_start', 'lan_dhcp_range_end'])
if len(valset.intersection(set(errors.keys()))) == 0:
    o = configfiles.EtcDhcp3DhcpConf()
    dhcp = o.subnets[ip_lan_network.strNormal()]
    dhcp.subnet   = ip_lan_network
    dhcp.netmask  = ip_lan_netmask
    dhcp.start_ip = ip_lan_network_range[int(lan_dhcp_range_start)]
    dhcp.end_ip   = ip_lan_network_range[int(lan_dhcp_range_end)]
    dhcp.options['routers'] = ip_lan_address.strNormal()
    dhcp.options['domain-name-servers'] = ip_lan_address.strNormal()
    o.write()

# write /etc/network/interfaces if no errors
# XXX assumes interfaces already exist: need method for creating them
valset = set(['wan_method', 'wan_address', 'wan_netmask', 'wan_gateway', \
        'lan_address', 'lan_netmask', 'lan_gateway'])
if len(valset.intersection(set(errors.keys()))) == 0:
    o = configfiles.EtcNetworkInterfaces()
    wan = o.ifaces['eth0']
    wan.iface = 'eth0'
    wan.method = wan_method
    if wan.method == 'static':
        wan.address = ip_wan_address
        wan.netmask = ip_wan_netmask
        wan.gateway = ip_wan_gateway
    lan = o.ifaces['eth1']
    lan.iface = 'eth1'
    lan.address = ip_lan_address
    lan.netmask = ip_lan_netmask
    lan.gateway = ip_lan_gateway
    o.write()

# XXX probably need to start/restart DHCP now, eh?

# redirect back to index, include all form values, plus error/info messages
qs = ''
for key in form.keys():
    qs = configfiles.appendQueryString(qs, key, form[key].value)

if len(errors) == 0:
    qs = configfiles.appendQueryString(qs, 'message', \
            'Your settings have been saved.')
else:
    # errors go back as key/val where key is the special prefix followed by
    # the control name, and val is the error message
    for key, value in errors.iteritems():
        qs = configfiles.appendQueryString(qs, ERR_PREFIX + key, value)
    qs = configfiles.appendQueryString(qs, 'message', 'There were errors...')

print "Location: /invnetwork/index.cgi?%s" % qs
print

