#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import with_statement

import os
import sys
import syslog
import traceback
import re
import subprocess as sp
from os import path
from sys import stderr,stdout

sys.path.append("/opt/inveneo/lib/python")

APT_DIRNAME="apt"
APT_REMOVE_CMD='apt-get -y --force-yes --purge remove '
APT_INSTALL_CMD='apt-get -y --force-yes install '
MAX_PACKAGES=30

package_matcher=re.compile(ur'^\s*(?!#)\s*(\S+)\s+(install|deinstall)(?:\s*|(?:\s+#.*))$')

def err(error):
    msg=error+"\n"
    syslog.syslog(msg)
    stderr.write(msg)

def generate_apt_commands(filename):
    installs=[]
    removes=[]
    
    try:
        with open(filename) as package_list:
            for line in package_list:
                match=package_matcher.match(line)
                if not match: continue # return if not match

                if match.group(2) == 'install':
                    installs.append(match.group(1))
                else:
                    removes.append(match.group(1))

    except Exception, ex:
        err(ex.message)

    commands=[]

    num_packages=0
    remove_cmd=None
    for package in removes:
        if not remove_cmd: remove_cmd = APT_REMOVE_CMD
        remove_cmd += package+" "
        num_packages += 1
        if num_packages == MAX_PACKAGES:
            commands.append(remove_cmd)
            num_packages=0
            remove_cmd=None
    if remove_cmd: commands.append(remove_cmd) # catch any left overs

    num_packages=0
    install_cmd=None
    for package in installs:
        if not install_cmd: install_cmd = APT_INSTALL_CMD
        install_cmd += package+" "
        num_packages += 1
        if num_packages == MAX_PACKAGES:
            commands.append(install_cmd)
            num_packages=0
            install_cmd=None
    if install_cmd: commands.append(install_cmd) # catch any left overs

    return commands
        


def main(dir_or_file):
    if not path.exists(dir_or_file):
        err("Can't read package directory/file: "+dir_or_file)
        return 2
    
    # set up list of files to process
    files=[]
    apt_dir=None
    
    if path.isfile(dir_or_file):
        apt_dir=path.join(path.dirname(dir_or_file), APT_DIRNAME)
        files.append(dir_or_file)
    else:
        apt_dir=path.join(dir_or_file, APT_DIRNAME)
        found_files=os.listdir(dir_or_file)
        found_files.sort()
        file_matcher=re.compile(ur'(^#.*)|(.*~$)')
        for name in found_files:
            full_name=path.join(dir_or_file,name)
            if (not file_matcher.match(name)) \
               and path.exists(full_name) \
               and path.isfile(full_name): files.append(full_name)

    # check if we have anything
    if len(files) == 0:
        err("No files found")
        return 3

    # copy apt config if found
    if path.exists(apt_dir):
        stdout.write('\nUpdating sources list and apt configuration...\n')
        sp.check_call(['cp','-r','-p',apt_dir,'/etc/']) # shutil not smart enough to copy just contents
        
    # set-up gpg keys
    stdout.write("\nUpdating GPG keys...\n")
    os.system("wget http://medibuntu.sos-sts.com/repo/medibuntu-key.gpg -O- | apt-key add - ")
    os.system("wget http://community.inveneo.org/apt/inveneo.gpg -O- | apt-key add - ")
    
    stdout.write("\nUpdating apt-cache...\n")
    sp.check_call(["/usr/bin/apt-get", "update"])

    commands=[]
    # now generate and issue the commands
    for package_list_filename in files:
        commands.extend(generate_apt_commands(package_list_filename))

    # now issue them
    for command in commands:
        stdout.write("Issuing command:\n"+command+"\n")
        os.system(command)
        stdout.write("\n\n")

    # do some clean up
    stdout.write("\nCleaning up APT cache\n")
    sp.call(['apt-get','-y','--force-yes','--purge','autoremove'])
    sp.call(['apt-get','-y','--purge','clean'])
    
    return 0
        
                
if __name__ == "__main__":
    syslog.openlog('install-packages.py', 0, syslog.LOG_LOCAL5)

    if len(sys.argv) != 2:
        err("Usage: install-packages.py <package list directory> | <markings file>")
        sys.exit(1)
    
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    sys.exit(main(path.abspath(sys.argv[1])))
