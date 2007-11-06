#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import syslog
import traceback
import subprocess as sp
from os import path
from sys import stdout, stderr
import pexpect

def main():
    syslog.openlog('populate-hub-ldap', 0, syslog.LOG_LOCAL5)
    INSTALL_DIR=path.dirname(path.dirname(path.abspath(sys.argv[0]))) 
 
    # restart slapd to get new config
    stdout.write("\nRestarting slapd to make sure gets new config...\n")
    sp.check_call(['/etc/init.d/slapd','restart'])
    
    # set up smbpasswd
    stdout.write('Establishing administrative passwd for Samba...\n')
    sp.check_call(['smbpasswd','-w','1nvene0'])
    
    # populate sldapd
    stdout.write('Populating default Samba values in LDAP server..\n')
    pexpect.run('smbldap-populate -u 10000 -g 10000',events={'ew password:':'1nvene0\n','type new password:':'1nvene0\n'})
    
    # adding permissions groups to ldap 
    stdout.write("\nAdding 'permissions' groups to ldap...\n")
    sp.check_call(['smbldap-migrate-unix-groups','-G',path.join(INSTALL_DIR,'permission-groups')])
    
    # Add default samba user
    try:
        sp.check_call(['inv-user-del.py','default']) 
    except Exception, ex:
        pass # don't care if user not there

    sp.check_call(['inv-user-create.py','--no-share','-u','1500','-c','Default User','-p','1nvene0','default'])
    
    # restart samba
    sp.check_call(['/etc/init.d/samba','restart'])
        
    return 0
    
        
                
if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/opt/inveneo/bin:/opt/inveneo/sbin'
    sys.exit(main())
