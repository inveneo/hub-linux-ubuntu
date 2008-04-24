#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
processForm.cgi

Copyright (c) 2007 Inveneo, inc. All rights reserved.
"""

# external modules
import sys
import os, string
import cgi
import cgitb; cgitb.enable()  # XXX remove this for production systems
from IPy import IP
from subprocess import Popen, PIPE

sys.path.append('/opt/inveneo/lib/python/inveneo')
import configfiles, processes

ERR_PREFIX = 'err_'

HOSTNAME_CHANGED    = 'hostname_changed'
DNS_CHANGED         = 'dns_changed'
LAN_ADDRESS_CHANGED = 'lan_address_changed'
DHCP_CHANGED        = 'dhcp_changed'

# CGI validation helpers
def required_single_word(name, default=None):
    """Returns valid word, else None.
    On error, puts error string in global errors list."""
    global form, errors
    value = form.getfirst(name, default)
    if value:
        if value.find(' ') >= 0:
            errors[name] = 'Cannot contain a space'
            value = None
    else:
        errors[name] = 'Required'
    return value

def required_ip(name, default=None):
    """Returns valid IP, else None.
    On error, puts error string in global errors list."""
    global form, errors
    value = form.getfirst(name, default)
    if value:
        try:
            value = IP(value)
        except:
            errors[name] = 'Invalid IP address'
            value = None
    else:
        errors[name] = 'Required'
    return value

def optional_ip(name, default=None):
    """Returns valid IP, else None.
    On error, puts error string in global errors list."""
    global form, errors
    value = form.getfirst(name, default)
    if value:
        try:
            value = IP(value)
        except:
            errors[name] = 'Invalid IP address'
            value = None
    return value

def choose_from_list(name, list, default=None):
    """Returns valid choice from provided list, else None.
    On error, puts error string in global errors list."""
    global form, errors
    value = form.getfirst(name, default)
    if not value.lower() in list:
        errors[name] = 'Value not in list'
        value = None
    return value

def optional_integer(name, default=None):
    """Returns valid integer, else None.
    On error, puts error string in global errors list."""
    global form, errors
    value = form.getfirst(name, default)
    if value:
        try:
            value = int(value)
        except:
            errors[name] = 'Invalid integer'
            value = None
    return value

# other helpers
def no_error_in_any_of(namelist):
    """Returns true if no name in list generated an error."""
    global errors
    return len(set(namelist).intersection(set(errors.keys()))) == 0

def get_network(ip_address, ip_netmask):
    """Given IP objects for address and netmask, return one for network.
    Return None if error."""
    try:
        ip_network = IP(ip_address.int() & ip_netmask.int())
    except:
        ip_network = None
    return ip_network

def str_or_empty(value):
    """Given a value or None, returns str(value) or empty string."""
    return [str(value), ''][value == None]

def execute(cmdlist):
    """Executes the given command line, returning stdout and stderr strings."""
    (sout, serr) = Popen(cmdlist, stdout=PIPE, stderr=PIPE).communicate() 
    return (sout, serr)

def trigger(flag_list):
    """Lets you know if any of the flags in your list are set."""
    global flags
    for flag in flag_list:
        if flag in flags:
            return True
    return False

# work sections
def validate_inputs():
    """Basic validation of individual input values."""

    global form, errors
    global hostname, ip_dns_0, ip_dns_1, wan_interface, wan_method
    global ip_wan_address, ip_wan_netmask, ip_wan_gateway
    global ppp_modem, ppp_phone, ppp_username, ppp_password
    global int_ppp_baud, int_ppp_idle_seconds, ppp_init1, ppp_init2
    global ip_lan_address, ip_lan_netmask, ip_lan_gateway
    global ip_lan_network, ip_lan_network_range
    global bool_lan_dhcp_on, int_lan_dhcp_range_start, int_lan_dhcp_range_end

    hostname = required_single_word('hostname')
    ip_dns_0 = required_ip('dns_0')
    ip_dns_1 = optional_ip('dns_1')

    wan_interface = choose_from_list('wan_interface', \
            ['off', 'ethernet', 'modem'])
    wan_method = choose_from_list('wan_method', ['dhcp', 'static'])
    if wan_method == 'static':
        ip_wan_address = required_ip('wan_address')
        ip_wan_netmask = required_ip('wan_netmask')
        ip_wan_gateway = required_ip('wan_gateway')
    else:
        ip_wan_address = optional_ip('wan_address')
        ip_wan_netmask = optional_ip('wan_netmask')
        ip_wan_gateway = optional_ip('wan_gateway')

    ppp_modem            = form.getfirst('ppp_modem')
    ppp_phone            = form.getfirst('ppp_phone')
    ppp_username         = form.getfirst('ppp_username')
    ppp_password         = form.getfirst('ppp_password')
    int_ppp_baud         = optional_integer('ppp_baud')
    int_ppp_idle_seconds = optional_integer('ppp_idle_seconds')
    ppp_init1            = form.getfirst('ppp_init1')
    ppp_init2            = form.getfirst('ppp_init2')

    ip_lan_address = required_ip('lan_address')
    ip_lan_netmask = required_ip('lan_netmask')
    ip_lan_gateway = required_ip('lan_gateway')
    bool_lan_dhcp_on = form.getfirst("lan_dhcp_on", "off").lower() == "on"
    int_lan_dhcp_range_start = optional_integer('lan_dhcp_range_start', '100')
    int_lan_dhcp_range_end = optional_integer('lan_dhcp_range_end', '200')

def business_logic():
    """Higher level 'business logic'."""

    global errors
    global ip_lan_address, ip_lan_netmask, ip_lan_gateway
    global ip_lan_network, ip_lan_network_range
    global bool_lan_dhcp_on, int_lan_dhcp_range_start, int_lan_dhcp_range_end

    ip_lan_network = get_network(ip_lan_address, ip_lan_netmask)
    if not ip_lan_network:
        errors['lan_network'] = 'Invalid LAN network'

    try:
        ip_lan_network_range = IP('%s/%s' % (ip_lan_network, ip_lan_netmask))
    except:
        errors['lan_network_range'] = 'Invalid LAN network range'

    if int_lan_dhcp_range_start:
        if (int_lan_dhcp_range_start < 1) or (254 < int_lan_dhcp_range_start):
            errors['lan_dhcp_range_start'] = 'Must be between 1 and 254'
    if int_lan_dhcp_range_end:
        if (int_lan_dhcp_range_end < 1) or (254 < int_lan_dhcp_range_end):
            errors['lan_dhcp_range_end'] = 'Must be between 1 and 254'
    if int_lan_dhcp_range_start and int_lan_dhcp_range_end:
        if (int_lan_dhcp_range_end <= int_lan_dhcp_range_start):
            errors['lan_dhcp_range_start'] = 'Must start before end'
            errors['lan_dhcp_range_end']   = 'Must end after start'

def rewrite_config_files(flags):
    """Rewrite the config files. Set flags for actions taken."""

    global errors
    global hostname, ip_dns_0, ip_dns_1, wan_interface, wan_method
    global ip_wan_address, ip_wan_netmask, ip_wan_gateway
    global ppp_modem, ppp_phone, ppp_username, ppp_password
    global int_ppp_baud, int_ppp_idle_seconds, ppp_init1, ppp_init2
    global ip_lan_address, ip_lan_netmask, ip_lan_gateway
    global ip_lan_network, ip_lan_network_range
    global bool_lan_dhcp_on, int_lan_dhcp_range_start, int_lan_dhcp_range_end

    # /etc/hostname
    o = configfiles.EtcHostname()
    previous_hostname = o.hostname
    if hostname != previous_hostname:
        o.hostname = hostname
        o.write()
        flags.add(HOSTNAME_CHANGED)
    else:
        flags.discard(HOSTNAME_CHANGED)

    # /etc/resolv.conf
    o = configfiles.EtcResolvConf()
    previous_nameservers = set(o.nameservers)
    current_nameservers = set()
    dns_0 = ip_dns_0.strNormal()
    current_nameservers.add(dns_0)
    if len(o.nameservers) > 0:
        o.nameservers[0] = dns_0
    else:
        o.nameservers.append(dns_0)
    if ip_dns_1:
        dns_1 = ip_dns_1.strNormal()
        current_nameservers.add(dns_1)
        if len(o.nameservers) > 1:
            o.nameservers[1] = dns_1
        else:
            o.nameservers.append(dns_1)
    if current_nameservers != previous_nameservers:
        flags.add(DNS_CHANGED)
    else:
        flags.discard(DNS_CHANGED)
    o.write()

    # /etc/hosts
    o = configfiles.EtcHosts()
    o.ips['127.0.1.1'] = \
            [hostname, hostname + '.local', hostname + '.localdomain']
    o.write()

    # /etc/wvdial.conf
    o = configfiles.EtcWvdialConf()
    o.metadata['modem']        = str_or_empty(ppp_modem)
    o.metadata['phone']        = str_or_empty(ppp_phone)
    o.metadata['username']     = str_or_empty(ppp_username)
    o.metadata['password']     = str_or_empty(ppp_password)
    o.metadata['baud']         = str_or_empty(int_ppp_baud)
    o.metadata['idle seconds'] = str_or_empty(int_ppp_idle_seconds)
    o.metadata['init1']        = str_or_empty(ppp_init1)
    o.metadata['init2']        = str_or_empty(ppp_init2)
    o.write()

    # /etc/ppp/peers/dod
    o = configfiles.EtcPppPeersDod()
    if ppp_modem:
        o.metadata['ttyname'] = ppp_modem
    if int_ppp_baud:
        o.metadata['speed'] = str(int_ppp_baud)
    if int_ppp_idle_seconds:
        o.metadata['idle'] = str(int_ppp_idle_seconds)
    o.write()

    # /etc/network/interfaces
    flags.discard(LAN_ADDRESS_CHANGED)
    o = configfiles.EtcNetworkInterfaces()
    if 'eth0' in o.ifaces:
        wan = o.ifaces['eth0']
    else:
        wan = o.add_iface('eth0', wan_method)
        wan.extras = [ \
                '  pre-up /opt/inveneo/sbin/wan-firewall.sh eth0 up', \
                '  post-down /opt/inveneo/sbin/wan-firewall.sh eth0 down']
    wan.iface = 'eth0'
    wan.method = wan_method
    if ip_wan_address: wan.address = ip_wan_address
    if ip_wan_netmask: wan.netmask = ip_wan_netmask
    if ip_wan_gateway: wan.gateway = ip_wan_gateway

    if 'eth1' in o.ifaces:
        lan = o.ifaces['eth1']
        if lan.address != ip_lan_address:
            flags.add(LAN_ADDRESS_CHANGED)
            old_ip_lan_address = lan.address
            old_ip_lan_netmask = lan.netmask
            old_ip_lan_gateway = lan.gateway
    else:
        lan = o.add_iface('eth1', 'static')
    lan.iface = 'eth1'
    lan.method = 'static'
    lan.address = ip_lan_address
    lan.netmask = ip_lan_netmask
    lan.gateway = ip_lan_gateway

    if not 'ppp0' in o.ifaces:
        ppp = o.add_iface('ppp0', 'ppp')
        ppp.extras = [ \
                '  pre-up /opt/inveneo/sbin/wan-firewall.sh ppp0 up', \
                '  post-down /opt/inveneo/sbin/wan-firewall.sh ppp0 down']

    o.autoset.discard('eth0')
    o.autoset.discard('ppp0')
    if wan_interface == 'ethernet':
        o.autoset.add('eth0')
    elif wan_interface == 'modem':
        o.autoset.add('ppp0')
    o.autoset.add('eth1')
    o.write()

    # /etc/dhcp3/dhcp.conf
    flags.discard(DHCP_CHANGED)
    o = configfiles.EtcDhcp3DhcpConf()
    lan_network = ip_lan_network.strNormal()
    lan_netmask = ip_lan_netmask.strNormal()
    if lan_network in o.subnets:
        dhcp = o.subnets[lan_network]
    else:
        dhcp = o.add_subnet(lan_network, lan_netmask)
        if trigger([LAN_ADDRESS_CHANGED]):
            # things are moving around...
            old_lan_network = get_network(old_ip_lan_address,
                        old_ip_lan_netmask).strNormal()
            o.subnets.pop(old_lan_network, None)
    dhcp.subnet   = ip_lan_network
    dhcp.netmask  = ip_lan_netmask
    dhcp.start_ip = ip_lan_network_range[int_lan_dhcp_range_start]
    dhcp.end_ip   = ip_lan_network_range[int_lan_dhcp_range_end]
    dhcp.options['routers'] = ip_lan_gateway.strNormal()
    dhcp.options['domain-name'] = '"local"'
    dhcp.options['domain-name-servers'] = ip_lan_address.strNormal()
    o.write()

def restart_services(flags):
    """Act on config file changes, guided by flags."""

    # get list of currently executing processes
    procs = processes.ProcSnap()

    # maybe reload the hostname
    if trigger([HOSTNAME_CHANGED]):
        (sout, serr) = execute(['/bin/hostname', '-F', '/etc/hostname'])
        if serr:
            errors['hostname'] = serr
            flags.discard(HOSTNAME_CHANGED)

    # maybe restart networking
    if trigger([HOSTNAME_CHANGED, LAN_ADDRESS_CHANGED]):
        script = '/etc/init.d/networking'
        (sout, serr) = execute([script, 'stop'])
        if not serr:
            (sout, serr) = execute([script, 'start'])

    '''
    # maybe restart the nameserver
    if trigger([DNS_CHANGED]):
        script = '/etc/init.d/bind9'
        (sout, serr) = execute([script, 'stop'])
        if not serr:
            (sout, serr) = execute([script, 'start'])
    '''

    # maybe restart the DHCP server
    if trigger([DHCP_CHANGED]):
        process = '/usr/sbin/dhcpd3'
        script  = '/etc/init.d/dhcp3-server'
        if procs.is_running(process):
            (sout, serr) = execute([script, 'stop'])
            if not serr:
                (sout, serr) = execute([script, 'start'])

    # maybe restart Samba
    if trigger([HOSTNAME_CHANGED, LAN_ADDRESS_CHANGED]):
        process = '/usr/sbin/smbd'
        script = '/etc/init.d/samba'
        if procs.is_running(process):
            (sout, serr) = execute([script, 'stop'])
            if not serr:
                (sout, serr) = execute([script, 'start'])

    # maybe restart Apache
    if trigger([LAN_ADDRESS_CHANGED]):
        process = '/usr/sbin/apache2'
        script = '/etc/init.d/apache2'
        if procs.is_running(process):
            (sout, serr) = execute([script, 'stop'])
            if not serr:
                (sout, serr) = execute([script, 'start'])

    # maybe restart Avahi
    # XXX how?

##
# START HERE
##
form = cgi.FieldStorage()
errors = {}
flags = set()

# uncomment this section for some debugging
#print "Content-Type: text/html"
#print
#for key in form.keys():
#    print '%s = "%s"<br>' % (key, form[key].value)

validate_inputs()
business_logic()
if len(errors) < 1:
    rewrite_config_files(flags)
    restart_services(flags)

# return all form values, plus error/info messages
qs = ''
for key in form.keys():
    qs = configfiles.appendQueryString(qs, key, form[key].value)

if len(errors) == 0:
    qs = configfiles.appendQueryString(qs, 'good_news', \
            'Your settings have been saved.')
else:
    # errors go back as key/val where key is the special prefix followed by
    # the control name, and val is the error message
    for key, value in errors.iteritems():
        qs = configfiles.appendQueryString(qs, ERR_PREFIX + key, value)
    qs = configfiles.appendQueryString(qs, 'bad_news', 'There were errors...')

# redirect to (possibly moved) webmin page
if trigger([LAN_ADDRESS_CHANGED]):
    urlbase = 'https://%s:10000' % ip_lan_address.strNormal()
else:
    urlbase = ''
print "Location: %s/invnetwork/index.cgi?%s" % (urlbase, qs)
print

