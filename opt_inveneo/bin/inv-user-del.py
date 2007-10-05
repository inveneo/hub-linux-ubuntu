#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import syslog
import subprocess as sp
from sys import stdout, stderr
from os import path


SMB_SHARE_TEMPLATE="/opt/inveneo/skeleton/samba/user.conf"
USER_SHARE_DIR="/etc/inveneo/samba/shares.d"
SHARES_SCRIPT="/etc/init.d/samba-shares.sh"

def usage():
    stderr.write("Usage: inv-user-del.py username\n")

def main():
    syslog.openlog('inv-user-del.py', 0, syslog.LOG_LOCAL5)
    
    if len(sys.argv) != 2:
        usage()
        return 2
        
    user_name=sys.argv[1]
        
    # remove user
    sp.check_call(['smbldap-userdel',user_name])
    
    # remove conf
    conf=path.join(USER_SHARE_DIR,user_name+'_docs.conf')
    try:
        os.remove(conf)
    except OSError, ex:
        err="Could not erase: "+conf
        syslog.syslog(err)
        stderr.write(err+'\n')
    
    # regenerate shares.conf and reload samba
    sp.check_call([SHARES_SCRIPT,'start'])
    sp.check_call(['/etc/init.d/samba','reload'])
  
    return 0
    
        
                
if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/opt/inveneo/bin:/opt/inveneo/sbin'
    sys.exit(main())
