#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import syslog
import traceback
import subprocess as sp
from os import path
from sys import stdout, stderr

def main():
    syslog.openlog('populate-hub-ldap', 0, syslog.LOG_LOCAL5)
    
    # restart slapd to get new config
    stdout.write("\nRestarting slapd to make sure gets new config...\n")
    sp.check_call(['/etc/init.d/slapd','restart'])
    
    # set up smbpasswd
    stdout.write('Establishing administrative passwd for Samba...\n')
    sp.check_call(['smbpasswd','-w','1nvene0'])
    
    # populate sldapd
    stdout.write('Populating default Samba values in LDAP server..\n')
    sp.check_call(['smbldap-populate','-u','10000','-g','10000'])
    
    # To Do: migrate, or create, global unix groups. 
    # problem is syncing them across all systems and _only_ need
    # 'permissions' groups like 'cdrom' and 'games' and only for user's logging in
    # on desktops using this db. so for now, don't do
    
    # sp.check_class(['smbldap-migrate-unix-groups','-G','/etc/group'])
    
    # Add default samba user
    sp.check_call(['inv-user-create.py','--no-share','-u','1500','-c','Default User','-p','1nvene0','default'])
    
    # restart samba
    sp.check_call(['/etc/init.d/samba-shares.d','reload'])
        
    return 0
    
        
                
if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/opt/inveneo/bin:/opt/inveneo/sbin'
    sys.exit(main())
