#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
processForm.cgi

Copyright (c) 2007 Inveneo, inc. All rights reserved.
"""

import os, sys, string
import cgi
import cgitb; cgitb.enable()  # XXX remove this for production systems

sys.path.append('/opt/inveneo/lib/python')
import netfiles

# START HERE
print "Content-Type: text/html"
print

form = cgi.FieldStorage()

for key in form.keys():
    print '%s = %s<br>' % (key, form[key].value)

# get submitted form values, or use their defaults
wan_type    = form.getfirst("wan_type", "")
wan_address = form.getfirst("wan_address", "")
wan_netmask = form.getfirst("wan_netmask", "")
wan_gateway = form.getfirst("wan_gateway", "")

ppp_modem        = form.getfirst("ppp_modem", "")
ppp_phone        = form.getfirst("ppp_phone", "")
ppp_username     = form.getfirst("ppp_username", "")
ppp_password     = form.getfirst("ppp_password", "")
ppp_baud         = form.getfirst("ppp_baud", "")
ppp_idle_seconds = form.getfirst("ppp_idle_seconds", "")
ppp_init1        = form.getfirst("ppp_init1", "")
ppp_init2        = form.getfirst("ppp_init2", "")

lan_address          = form.getfirst("lan_address", "")
lan_address_orig     = form.getfirst("lan_address_orig", "")
lan_netmask          = form.getfirst("lan_netmask", "")
lan_netmask_orig     = form.getfirst("lan_netmask_orig", "")
lan_dhcp_on          = form.getfirst("lan_dhcp_on", "")
lan_dhcp_range_start = form.getfirst("lan_dhcp_range_start", "")
lan_dhcp_range_end   = form.getfirst("lan_dhcp_range_end", "")

# XXX validate the submitted form values!!!

o = netfiles.EtcNetworkInterfaces()
print o.filepath + "<br>"

o = netfiles.EtcWvdialConf()
o.metadata['modem']        = ppp_modem
o.metadata['phone']        = ppp_phone
o.metadata['username']     = ppp_username
o.metadata['password']     = ppp_password
o.metadata['baud']         = ppp_baud
o.metadata['idle seconds'] = ppp_idle_seconds
o.metadata['init1']        = ppp_init1
o.metadata['init2']        = ppp_init2
print "<pre>%s</pre><br>" % str(o)
#o.write()

o = netfiles.EtcDhcp3DhcpConf()
print "<pre>%s</pre><br>" % str(o)

print "<h3>DONE</h3>"
print "<a href='/invnetwork/'>Return to Network Management</a>"
