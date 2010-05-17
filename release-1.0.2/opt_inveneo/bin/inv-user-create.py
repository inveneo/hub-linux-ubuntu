#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import syslog
import traceback
import getopt
import subprocess as sp
from os import path
from sys import stdout, stderr

OTHER_GROUPS='adm,dialout,fax,voice,cdrom,floppy,audio,dip,video,plugdev,games,lpadmin,scanner,fuse'
DEFAULT_GROUP='inveneo_users'
SKELETON_DIR='/opt/inveneo/skeleton/samba/user-share-dir'
HOME_DIR_BASE='/srv/samba/user_shares'
ADD_CMD_BASE="smbldap-useradd -a -n -g "+DEFAULT_GROUP+" -G "+OTHER_GROUPS+" -d "+HOME_DIR_BASE+"/%(user_name)s"
ADD_HOME_DIR=" -m -k "+SKELETON_DIR

SMB_SHARE_TEMPLATE="/opt/inveneo/skeleton/samba/user.conf"
USER_SHARE_DIR="/etc/inveneo/samba/shares.d"
SHARES_SCRIPT="/etc/init.d/samba-shares.sh"

def usage():
    """docstring for fname"""
    stderr.write("Usage: inv-user-create.py [-u <uid>] [-c <real name>] [-p <passwd>] [--no-share] username\n")

def main():
    syslog.openlog('inv-create-user', 0, syslog.LOG_LOCAL5)
    
    opts=None
    args=None
    
    try:
        opts, args=getopt.getopt(sys.argv[1:],'u:c:p:',['no-share'])
    except Exception, ex:
        usage()
        return 2
    
    # do we have a username?
    if len(args) != 1:
        usage()
        return 3
    user_name=args[0]
        
    # construct useradd call
    user_add_cmd=ADD_CMD_BASE
    password=None
    no_share=False
    real_name=None
    uid=None
    for o, a in opts:
        if o == "--no-share":
            no_share=True
        elif o == "-u" and len(a.strip()) != 0:
            uid = int(a)
        elif o == "-c" and len(a.strip()) != 0:
            real_name=a
        elif o == "-p" and len(a.strip()) != 0:
            password = a

    if uid: user_add_cmd += " -u %d" % uid
    if real_name: user_add_cmd += ' -c "%s"' % real_name
    if not no_share: user_add_cmd += ADD_HOME_DIR
    user_add_cmd += " %(user_name)s"
    cmd = user_add_cmd % {'user_name':user_name}
    syslog.syslog("issuing cmd: "+cmd)
    ret=os.system(cmd)
    if ret != 0:
        stderr('failed to add user: '+user_name)
        return 4
        
    # set password, if provided
    if password:
        sp.check_call(['inv-passwd.py','-u',user_name,'-p', password])
    
    # create share
    if not no_share:
        os.system('sed "s/%%USERNAME%%/%(user)s/g" %(tmpl)s > %(share_dir)s/%(user)s_docs.conf' % \
            {'user':user_name, 'tmpl':SMB_SHARE_TEMPLATE,'share_dir':USER_SHARE_DIR})
        sp.check_call([SHARES_SCRIPT,'start'])
        sp.check_call(['/etc/init.d/samba','reload'])
  
    return 0
    
        
                
if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/opt/inveneo/bin:/opt/inveneo/sbin'
    sys.exit(main())
