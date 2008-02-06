#!/usr/bin/env python

# process.cgi - process the form on index.html

import os, sys, string
import cgi

import cgitb; cgitb.enable()  # XXX remove this for production systems

# START HERE
print "Content-Type: text/html"
print

form = cgi.FieldStorage()

for key in form.keys():
    print '%s = %s<br>' % (key, form[key].value)

# get submitted form values, or use their defaults
wan_type       = form.getfirst("wan_type", "")
wan_address    = form.getfirst("wan_address", "")
wan_netmask    = form.getfirst("wan_netmask", "")
wan_gateway    = form.getfirst("wan_gateway", "")
lan_address    = form.getfirst("lan_address", "")
lan_dhcp_on    = form.getfirst("lan_dhcp_on", "")
lan_dhcp_range = form.getfirst("lan_dhcp_range", "")

# XXX validate the submitted form values
"""
wan_type = dhcp
wan_address = wan address
wan_netmask = wan netmask
wan_gateway = wan gateway
ppp_phone = 5551212
ppp_username = username
ppp_password = password
ppp_baud = 460800
ppp_idle_seconds = 300
ppp_init1 = ATZ
ppp_init2 = ATQ0 V1 E1 S0=0 &C1 &D2 +FCLASS=0
lan_address = 192.168.100.1
lan_netmask = 255.255.255.0
lan_dhcp_on = on
lan_dhcp_range_start = 100
lan_dhcp_range_end = 200
"""
