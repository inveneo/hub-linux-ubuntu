#!/usr/bin/env python

# process.cgi - process the form on index.html

import os, sys, string
import cgi

import cgitb; cgitb.enable()  # XXX remove this for production systems

# START HERE
print "Content-Type: text/html"
print

form = cgi.FieldStorage()
#for key in form.keys():
#    print '%s = %s<br>' % (key, form[key].value)

# get submitted form values, or use their defaults
wan_type       = form.getfirst("wan_type", "")
wan_address    = form.getfirst("wan_address", "")
wan_netmask    = form.getfirst("wan_netmask", "")
wan_gateway    = form.getfirst("wan_gateway", "")
lan_address    = form.getfirst("lan_address", "")
lan_dhcp_on    = form.getfirst("lan_dhcp_on", "")
lan_dhcp_range = form.getfirst("lan_dhcp_range", "")

# XXX validate the submitted form values

print "<h3>not yet implemented</h3>"
