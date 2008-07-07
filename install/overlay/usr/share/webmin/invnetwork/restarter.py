#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
restarter.py

Restarts services as given by command line args.  This script can
be nohup'd so it runs to completion despite lost web connection.

Copyright (c) 2008 Inveneo, inc. All rights reserved.
"""

import sys, os, time
from IPy import IP
from subprocess import Popen, PIPE
from inveneo import configfiles, processes

LOGDIR = '/var/log/webmin'

APACHE_BIN   = '/usr/sbin/apache2'
APACHE_CTL   = '/etc/init.d/apache2'
SAMBA_BIN    = '/usr/sbin/smbd'
SAMBA_CTL    = '/etc/init.d/samba'
SQUID_BIN    = '/usr/sbin/squid3'
SQUID_CTL    = '/etc/init.d/squid3'
DHCP_BIN     = '/usr/sbin/dhcpd3'
DHCP_CTL     = '/etc/init.d/dhcp3-server'
DNS_BIN      = '/usr/sbin/named'
DNS_CTL      = '/etc/init.d/bind9'
NETWORK_CTL  = '/etc/init.d/networking'
HOSTNAME_BIN = '/bin/hostname'

SPECIAL_LAN_NAME = 'lan-ip-do-not-edit'

def execute(cmdlist):
    """Executes the given command line.
    Logs output.
    Returns stdout and stderr strings."""
    global fout

    fout.write('=== Command = %s\n' % str(cmdlist))
    (sout, serr) = Popen(cmdlist, stdout=PIPE, stderr=PIPE).communicate() 
    fout.write('--- stdout: ---\n%s\n' % sout)
    fout.write('--- stderr: ---\n%s\n' % serr)
    return (sout, serr)

def main(tasks):
    """Shut down services in order; restart them in reverse order."""

    # some tasks may cause execution of others
    if 'hostname' in tasks:
        tasks.append('networking')
    if 'networking' in tasks:
        # tasks.append('dns')
        tasks.append('dhcp')
        tasks.append('samba')
        tasks.append('apache')

    # get snapshot of pre-shutdown processes
    procSnap = processes.ProcSnap()

    # shut off services in order
    if ('apache' in tasks) and procSnap.is_running(APACHE_BIN):
        execute([APACHE_CTL, 'stop'])

    if ('samba' in tasks) and procSnap.is_running(SAMBA_BIN):
        execute([SAMBA_CTL, 'stop'])

    if ('squid' in tasks) and procSnap.is_running(SQUID_BIN):
        execute([SQUID_CTL, 'stop'])

    if (('dhcp' in tasks) or \
        ('dhcp_stop' in tasks) or \
        ('dhcp_restart' in tasks)) and \
        procSnap.is_running(DHCP_BIN):
        execute([DHCP_CTL, 'stop'])

    if ('dns' in tasks) and procSnap.is_running(DNS_BIN):
        execute([DNS_CTL, 'stop'])

    if 'networking' in tasks:
        execute([NETWORK_CTL, 'stop'])

    # hostname only changes when all is quiet
    if 'hostname' in tasks:
        execute([HOSTNAME_BIN, '-F', '/etc/hostname'])

    # /etc/hosts only changes when all is quiet
    if 'networking' in tasks:
        hostname = configfiles.EtcHostname().hostname
        ifaces = configfiles.EtcNetworkInterfaces().ifaces
        lan_address = None
        if 'eth1' in ifaces:
            lan_address = ifaces['eth1'].address

        # fix /etc/hosts
        o = configfiles.EtcHosts()
        o.ips['127.0.1.1'] = \
                [hostname, hostname + '.local', hostname + '.localdomain']
        for addr in o.ips.keys():
            nameset = set(o.ips[addr])
            print "nameset =", nameset
            nameset.discard(SPECIAL_LAN_NAME)
            print "nameset =", nameset
            if len(nameset):
                o.ips[addr] = [name for name in nameset]
            else:
                del o.ips[addr]
        if lan_address:
            names = o.ips.get(lan_address.strNormal(), [])
            o.ips[lan_address.strNormal()] = names + [SPECIAL_LAN_NAME]
        o.write()

    # start up services in order
    if 'networking' in tasks:
        execute([NETWORK_CTL, 'start'])

    if ('dns' in tasks) and procSnap.is_running(DNS_BIN):
        execute([DNS_CTL, 'start'])

    if ('dhcp' in tasks) or \
       ('dhcp_start' in tasks) or \
       ('dhcp_restart' in tasks):
        execute([DHCP_CTL, 'start'])

    if ('squid' in tasks) and procSnap.is_running(SQUID_BIN):
        execute([SQUID_CTL, 'start'])

    if ('samba' in tasks) and procSnap.is_running(SAMBA_BIN):
        execute([SAMBA_CTL, 'start'])

    if ('apache' in tasks) and procSnap.is_running(APACHE_BIN):
        execute([APACHE_CTL, 'start'])

# use a special, short logfile (no need to rotate)
if not os.path.isdir(LOGDIR):
    os.mkdir(LOGDIR)
logfile = os.path.splitext(os.path.basename(sys.argv[0]))[0] + '.log'
fout = open(os.path.join(LOGDIR, logfile), 'w')
fout.write(time.asctime() + '\n')

# arguments are names of tasks (including services to restart)
tasks = sys.argv[1:]
fout.write('Tasks: %s\n' % str(tasks))

try:
    main(tasks)
except:
    traceback.print_exc(file = fout)

# close logfile
fout.close()

