#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
processForm.cgi

Copyright (c) 2007 Inveneo, inc. All rights reserved.
"""

# external modules
import sys
sys.path.append('/opt/inveneo/lib/python/inveneo')
import os, string
import cgi
import cgitb; cgitb.enable()  # XXX remove this for production systems
from IPy import IP
from subprocess import Popen, PIPE
import configfiles

ERR_PREFIX = 'err_'
errors = {}
form = cgi.FieldStorage()

# uncomment this section for some debugging
#print "Content-Type: text/html"
#print
#for key in form.keys():
#    print '%s = "%s"<br>' % (key, form[key].value)

##
# Basic validation of individual values
##
hostname = form.getfirst("hostname", "hub-server")
if hostname == '':
    errors['hostname'] = 'Invalid hostname'
elif len(hostname.split()) > 1:
    errors['hostname'] = 'Invalid hostname'
hostname_previous = form.getfirst("hostname_previous", None)

wan_interface = form.getfirst("wan_interface", "").lower()
if not wan_interface in ['off', 'ethernet', 'modem']:
    errors['wan_interface'] = 'Invalid WAN interface'
wan_method = form.getfirst("wan_method", "").lower()
if not wan_method in ['dhcp', 'static']:
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

bool_lan_dhcp_on = form.getfirst("lan_dhcp_on", "off") == "on"

lan_dhcp_range_start = form.getfirst("lan_dhcp_range_start", "100").lower()
i = 0
try:
    i = int(lan_dhcp_range_start)
except:
    errors['lan_dhcp_range_start'] = 'Must be an integer'
if (i < 1) or (254 < i):
    errors['lan_dhcp_range_start'] = 'Must be between 1 and 254'

lan_dhcp_range_end = form.getfirst("lan_dhcp_range_end", "200").lower()
i = 0
try:
    i = int(lan_dhcp_range_end)
except:
    errors['lan_dhcp_range_end'] = 'Must be an integer'
if (i < 1) or (254 < i):
    errors['lan_dhcp_range_end'] = 'Must be between 1 and 254'

##
# Higher level "business" logic
##
try:
    ip_lan_network = IP(ip_lan_address.int() & ip_lan_netmask.int())
except:
    errors['lan_network'] = 'Invalid network'
try:
    ip_lan_network_range = IP('%s/%s' % (ip_lan_network, ip_lan_netmask))
except:
    errors['lan_network_range'] = 'Invalid network range'

##
# Write the config files (when no errors were found in their values)
##

# hostname
if hostname_previous and hostname_previous != hostname and \
        'hostname' not in errors.keys():
    o = configfiles.EtcHostname()
    o.hostname = hostname
    o.write()
    (sout, serr) = Popen(['/bin/hostname', '-F', '/etc/hostname'],
            stdout=PIPE, stderr=PIPE).communicate() 
    if serr:
        errors['hostname'] = serr

# /etc/resolv.conf
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

# /etc/wvdial.conf
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

# /etc/network/interfaces
lan_address_changed = False
valset = set(['wan_method', 'wan_address', 'wan_netmask', 'wan_gateway', \
        'lan_address', 'lan_netmask', 'lan_gateway'])
if len(valset.intersection(set(errors.keys()))) == 0:
    o = configfiles.EtcNetworkInterfaces()
    if o.ifaces.has_key('eth0'):
        wan = o.ifaces['eth0']
    else:
        wan = o.add_iface('eth0', wan_method)
        wan.extras = ['  pre-up /opt/inveneo/sbin/wan-firewall.sh eth0 up', \
                      '  post-down /opt/inveneo/sbin/wan-firewall.sh eth0 down']
    wan.iface = 'eth0'
    wan.method = wan_method
    wan.address = ip_wan_address
    wan.netmask = ip_wan_netmask
    wan.gateway = ip_wan_gateway

    if o.ifaces.has_key('eth1'):
        lan = o.ifaces['eth1']
        if lan.address != ip_lan_address:
            lan_address_changed = True
    else:
        lan = o.add_iface('eth1', 'static')
    lan.iface = 'eth1'
    lan.method = 'static'
    lan.address = ip_lan_address
    lan.netmask = ip_lan_netmask
    lan.gateway = ip_lan_gateway

    o.autoset.discard('eth0')
    o.autoset.discard('ppp0')
    if wan_interface == 'ethernet':
        o.autoset.add('eth0')
    elif wan_interface == 'modem':
        o.autoset.add('ppp0')
    o.autoset.add('eth1')

    o.write()

# /etc/dhcp3/dhcp.conf
valset = set(['lan_address', 'lan_netmask', 'lan_network', 'lan_gateway', \
        'lan_dhcp_range_start', 'lan_dhcp_range_end'])
if len(valset.intersection(set(errors.keys()))) == 0:
    o = configfiles.EtcDhcp3DhcpConf()
    lan_network = ip_lan_network.strNormal()
    lan_netmask = ip_lan_netmask.strNormal()
    if o.subnets.has_key(lan_network):
        dhcp = o.subnets[lan_network]
    else:
        dhcp = o.add_subnet(lan_network, lan_netmask)
    dhcp.subnet   = ip_lan_network
    dhcp.netmask  = ip_lan_netmask
    dhcp.start_ip = ip_lan_network_range[int(lan_dhcp_range_start)]
    dhcp.end_ip   = ip_lan_network_range[int(lan_dhcp_range_end)]
    dhcp.options['routers'] = ip_lan_gateway.strNormal()
    dhcp.options['domain-name'] = '"local"'
    dhcp.options['domain-name-servers'] = ip_lan_address.strNormal()
    o.write()

##
# Act on config file changes
##

# XXX start/restart/stop DHCP server
command = "/etc/init.d/dhcp3-server"
if bool_lan_dhcp_on:
    arg = "force-reload"
else:
    arg = "stop"
#(sout, serr) = Popen([command, arg], stdout=PIPE, stderr=PIPE).communicate() 
#errors['lan_dhcp_on'] = "sout='%s', serr='%s'" % (sout, serr)

##
# Return to Webmin
##

# return all form values, plus error/info messages
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

# redirect to (possibly moved) webmin page
if lan_address_changed:
    urlbase = 'http://%s:10000' % ip_lan_address.strNormal()
else:
    urlbase = ''
print "Location: %s/invnetwork/index.cgi?%s" % (urlbase, qs)
print

