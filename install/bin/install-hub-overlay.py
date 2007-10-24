#!/usr/bin/env python
# encoding: utf-8
"""
install-hub-overlay.py

Created by Jeff Wishnie on 2007-10-03.
Copyright (c) 2007 Inveneo, inc. All rights reserved.
"""

from __future__ import with_statement

import os
import sys
import syslog
import traceback
import re
import pwd
import subprocess as sp
from os import path
from sys import stderr,stdout


SERVICES=('asterisk','samba','samba-shares.sh','slapd','squid3','dhcp3-server', \
          'apache2','avahi-daemon','cupsys','mysql','webmin')

# Folder walking 'cause os.path functions aren't recursive 
def folder_visitor(func, dirname, fnames):
    """This function is used as a visitor in a 'walk'
    'func' is a lambda that is applied to the current dir and
    any files in the dir. It is not applied to sub-folders in fnames as
    it will get called when it descends"""
    
    func(dirname)
    
    for entry in fnames:
        full_name=path.join(dirname,entry)
        if path.isfile(full_name): func(full_name)
        
def fix_perms(opt_root):
    """docstring for fix_perms"""
    # fix samba shared docs
    os.chmod(path.join(opt_root,"install","overlay","srv","samba","shared_docs"),0777)

    # fix /etc/libnss-ldap.secret
    os.chmod(path.join(opt_root,"install","overlay","etc","libnss-ldap.secret"),0600)
    
         
######## transfer event helpers #########
def fix_owners(opt_root):
    """docstring for fix_owners"""
    # Globally switch ownership of overlay to root
    uinfo=pwd.getpwnam('root')
    path.walk(path.join(opt_root,'install','overlay'), \
         folder_visitor, \
         lambda f: os.chown(f, uinfo[2],uinfo[3]))
    
def pre_overlay_transfer(overlay_root, dest):
    """docstring for pre_overlay_transfer"""

    # stop services
    for service in SERVICES:
        try:
            sp.call(['/etc/init.d/'+service,'stop'])
        except Exception, ex:
            stderr.write("Failed to stop: "+service+"\n")

    # remove /etc/rc2.d/S12hal which needs to be moved to S13hal
    try:
        os.remove("/etc/rc2.d/S12hal")
    except OSError, ex:
        pass # silent, must not have been there
    
def post_overlay_transfer(overlay_root, dest):
    # HACK: Fix Squid perms 
    uinfo=pwd.getpwnam('proxy')
    path.walk(path.join(dest,'var','log','squid3'), \
        folder_visitor, \
        lambda f: os.chown(f, uinfo[2],uinfo[3]))

    # install new initramfs - we need the scripts to handle raid drives
    sp.check_call(['update-initramfs','-k','all','-u'])

    # start-up services (in reverse order of stop)
    for service in SERVICES[::-1]:
        try:
            stdout.write("Attempting to start: "+service+"\n")
            sp.call(['/etc/init.d/'+service,'start'])
        except Exception, ex:
            stderr.write("Failed to start: "+service+"\n")
    
def transfer_overlay(src,dest):
    """docstring for transfr_overlay"""
    cur_dir=os.getcwdu()
    os.chdir(src)
    os.system("find . -name .svn -prune -o -print0 | cpio --null -pvud "+dest)
    os.chdir(cur_dir)

def make_links(dest):
    """docstring for make_links"""
    pass


def main():
    syslog.openlog('install-hub-overlay', 0, syslog.LOG_LOCAL5)
    
    # get useful paths
    install_root=path.dirname(path.dirname(path.abspath(sys.argv[0])))
    opt_root=path.dirname(install_root)
    overlay_root=path.join(install_root, "overlay")
    overlay_dest='/'
    
    stdout.write('\nFixing ownership in: '+opt_root+'...\n')
    fix_owners(opt_root)
    
    stdout.write('\nFixing Permissions in: '+opt_root+'...\n')
    fix_perms(opt_root)
    
    stdout.write('\nRunning pre-transfer processing...\n')
    pre_overlay_transfer(overlay_root, overlay_dest)
    
    stdout.write('\nTransfering overlay files to root (/)...\n')
    transfer_overlay(overlay_root, overlay_dest)
    
    stdout.write('\nSetting up any missing symlinks in destination...\n')
    make_links(overlay_dest)
    
    stdout.write('\nRunning post-transfer processing...\n')
    post_overlay_transfer(overlay_root, overlay_dest)
    
    return 0

if __name__ == '__main__':
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    sys.exit(main())

