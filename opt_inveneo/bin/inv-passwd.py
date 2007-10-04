#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import syslog
import traceback
import getopt
import subprocess as sp
from os import path
from sys import stdout, stderr
import pexpect

def usage():
    """docstring for fname"""
    stderr.write("Usage: inv-passwd.py -u <username> -p <password>\n")

def main():
    syslog.openlog('inv-passwd.py', 0, syslog.LOG_LOCAL5)
    
    opts=None
    args=None
    
    try:
        opts, args=getopt.getopt(sys.argv[1:],'u:p:')
    except Exception, ex:
        usage()
        return 2
    
    user_name=None
    password=None
    for o, a in opts:
        if o == "-p" and len(a.strip()) !=0:
            password=a
        elif o == "-u" and len(a.strip()) !=0:
            user_name =a

    if user_name == None or password == None:
        usage()
        return 3
        
    output, exit = pexpect.run('smbldap-passwd '+user_name, withexitstatus=True, events={'New password':password+'\n', 'type new password':password+'\n'})
    return exit
    
        
                
if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/opt/inveneo/bin:/opt/inveneo/sbin'
    sys.exit(main())
