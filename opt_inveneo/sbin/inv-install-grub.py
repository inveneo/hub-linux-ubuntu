#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import syslog
import traceback
import subprocess as sp
from os import path
from sys import stdout, stderr
from inveneo import constants

ENV = ['env', constants.INV_LANG_EN]

GRUB='/usr/sbin/grub'
    
def write_msg(msg, console=stdout):
    syslog.syslog(msg)
    console.write(msg+"\n")

def main(target_device):
    syslog.openlog('inv-install-grub', 0, syslog.LOG_LOCAL5)

    write_msg("Installing GRUB on new drive %s" % target_device)
    command = [GRUB, '--batch']
#    child = sp.Popen(ENV + command, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT)
    child = sp.Popen(ENV + command, stdin=sp.PIPE, stdout=sp.PIPE)
    child.stdin.write("device (hd0) %s\n" % target_device)
    child.stdin.write("root (hd0,0)\n")
    child.stdin.write("setup (hd0)\n")
    child.stdin.write("quit\n")
    print child.communicate()[0]
    return 0

if __name__ == "__main__":
    # sanitize PATH
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/opt/inveneo/bin:/opt/inveneo/sbin'
    sys.exit(main(sys.argv[1]))
