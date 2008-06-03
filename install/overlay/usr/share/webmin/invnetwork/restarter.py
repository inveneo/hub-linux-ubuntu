#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
restarter.py

Restarts services as given by command line args.  This script can
be nohup'd so it runs to completion despite lost web connection.

Copyright (c) 2008 Inveneo, inc. All rights reserved.
"""

import sys
from subprocess import Popen, PIPE, call
from inveneo import processes

def execute(cmdlist):
    """Executes the given command line, returning stdout and stderr strings."""
    print cmdlist
    (sout, serr) = Popen(cmdlist, stdout=PIPE, stderr=PIPE).communicate() 
    print (sout, serr)
    return (sout, serr)

def stop_start(script):
    """Stops service via given init script: if no errors, starts again."""
    (sout, serr) = execute([script, 'stop'])
    (sout, serr) = execute([script, 'start'])

# arguments are names of tasks (including services to restart)
taskset = set(['hostname', 'networking', 'bind', 'dhcp_stop', 'dhcp_start',
    'dhcp_restart', 'samba', 'apache'])
tasks = sys.argv[1:]
for task in tasks:
    if not task in taskset:
        print 'Usage: %s %s' % (sys.argv[0], str(list(taskset)))

# get list of currently executing processes
procs = processes.ProcSnap()

# maybe reload the hostname
if 'hostname' in tasks:
    cmdlist = ['/bin/hostname', '-F', '/etc/hostname']
    (sout, serr) = execute(cmdlist)

# maybe restart networking
# this also does avahi
if 'networking' in tasks:
    stop_start('/etc/init.d/networking')

# maybe restart the nameserver
if 'bind' in tasks:
    stop_start('/etc/init.d/bind9')

# maybe stop/start/restart the DHCP server
if procs.is_running('/usr/sbin/dhcpd3'):
    if 'dhcp_stop' in tasks:
        call(['/etc/init.d/dhcp3-server', 'stop'])
    elif 'dhcp_restart' in tasks:
        call(['/etc/init.d/dhcp3-server', 'restart'])
else:
    if 'dhcp_start' in tasks:
        call(['/etc/init.d/dhcp3-server', 'start'])

# maybe restart Samba
if 'samba' in tasks:
    if procs.is_running('/usr/sbin/smbd'):
        stop_start('/etc/init.d/samba')

# maybe restart Apache
if 'apache' in tasks:
    if procs.is_running('/usr/sbin/apache2'):
        stop_start('/etc/init.d/apache2')

