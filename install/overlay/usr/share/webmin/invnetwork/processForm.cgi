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

sys.path.append('/opt/inveneo/lib/python')
import configfiles

# START HERE
print "Content-Type: text/html"
print

form = cgi.FieldStorage()

for key in form.keys():
    print '%s = %s<br>' % (key, form[key].value)

# get submitted form values, or use their defaults
wan_interface = form.getfirst("wan_interface", "")
wan_method    = form.getfirst("wan_method", "")
wan_address   = form.getfirst("wan_address", "")
wan_netmask   = form.getfirst("wan_netmask", "")
wan_gateway   = form.getfirst("wan_gateway", "")

ppp_modem        = form.getfirst("ppp_modem", "")
ppp_phone        = form.getfirst("ppp_phone", "")
ppp_username     = form.getfirst("ppp_username", "")
ppp_password     = form.getfirst("ppp_password", "")
ppp_baud         = form.getfirst("ppp_baud", "")
ppp_idle_seconds = form.getfirst("ppp_idle_seconds", "")
ppp_init1        = form.getfirst("ppp_init1", "")
ppp_init2        = form.getfirst("ppp_init2", "")

lan_address          = IP(form.getfirst("lan_address", "192.168.100.1"))
lan_netmask          = IP(form.getfirst("lan_netmask", "255.255.255.0"))
lan_gateway          = IP(form.getfirst("lan_gateway", "192.168.100.1"))
lan_dhcp_on          = form.getfirst("lan_dhcp_on", "")
lan_dhcp_range_start = form.getfirst("lan_dhcp_range_start", "")
lan_dhcp_range_end   = form.getfirst("lan_dhcp_range_end", "")

# XXX validate the submitted form values!!!

lan_network = IP(lan_address.int() & lan_netmask.int())
lan_network_range = IP('%s/%s' % (lan_network, lan_netmask))

o = configfiles.EtcWvdialConf()
o.metadata['modem']        = ppp_modem
o.metadata['phone']        = ppp_phone
o.metadata['username']     = ppp_username
o.metadata['password']     = ppp_password
o.metadata['baud']         = ppp_baud
o.metadata['idle seconds'] = ppp_idle_seconds
o.metadata['init1']        = ppp_init1
o.metadata['init2']        = ppp_init2
#print "<pre>%s</pre><br>" % str(o)
#o.write()

# XXX assumes subnets already exist: need method for creating them
o = configfiles.EtcDhcp3DhcpConf()
dhcp = o.subnets[lan_network.strNormal()]
dhcp.subnet   = lan_network
dhcp.netmask  = lan_netmask
dhcp.start_ip = lan_network_range[int(lan_dhcp_range_start)]
dhcp.end_ip   = lan_network_range[int(lan_dhcp_range_end)]
dhcp.options['routers'] = lan_address.strNormal()
dhcp.options['domain-name-servers'] = lan_address.strNormal()
#print "<pre>%s</pre><br>" % str(o)
#o.write()

o = configfiles.EtcNetworkInterfaces()
wan = o.ifaces['eth0']
wan.iface = 'eth0'
print "WAN METHOD =", wan_method
wan.method = wan_method
wan.address = wan_address
wan.netmask = wan_netmask
wan.gateway = wan_gateway
lan = o.ifaces['eth1']
lan.iface = 'eth1'
lan.address = lan_address
lan.netmask = lan_netmask
lan.gateway = lan_gateway
print "<pre>%s</pre><br>" % str(o)
#o.write()

# XXX probably need to restart DHCP now, eh?

# redirect back to index
#query_string = "message=Not+Implemented"
#print "Location: /invnetwork/index.cgi?%s" % query_string
#print

print "<h3>DONE</h3>"
print "<a href='/invnetwork/'>Return to Network Management</a>"

