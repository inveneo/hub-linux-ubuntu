#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import sys
import syslog
import re
import subprocess as sp
#from inveneo import constants, raidutils, fileutils, diskutils


class CheckSwap:
    def __init__(self):
        self.matcher=re.compile(r'^\s*(\S+)\s+\S+\s+swap\s+',re.M)
        pass	

    def main(self,fstab):
        """ 
        Check fstab for swap partition, then make sure swap is active. 
        It's an imaging repair--as swap partitions don't need to be copied in an
        image.
        """
        
        syslog.openlog('inv-check-swap', 0, syslog.LOG_LOCAL5)

        # try to open FSTAB
        try:
            with open(fstab) as f:
                buf=f.read()
        except:
            mess="Cannot open: %s" % fstab
            sys.stderr.write(mess+"\n")
            syslog.syslog(mess)
            return (1)
            
        # find swap entry... go with first   
        match=self.matcher.search(buf)
        if match==None:
            mess="No 'swap' entry found in fstab: %s" % fstab
            sys.stderr.write(mess+"\n")
            syslog.syslog(mess)
            return 2
            
        swap_dev=match.groups()[0].lower()
        
        # see if it is in UUID style
        if swap_dev.startswith('uuid'):
            id=swap_dev.split('=')[1]
            swap_dev=sp.Popen(['readlink','-f','/dev/disk/by-uuid/'+id],stdout=sp.PIPE).communicate()[0].strip()
            
        # try mkswap/swapon
        sp.Popen(['mkswap',swap_dev],stdout=sp.PIPE).communicate()
        sp.Popen(['swapon','-a'],stdout=sp.PIPE).communicate()
        
        return 0
                
if __name__ == '__main__':
    if len(sys.argv) > 2:
        sys.stderr.write("Usage: inv-check-swap.py <path-to-fstab> (defaults to /etc/fstab)>\n")
        sys.exit(1)
    
    fstab='/etc/fstab'
    if len(sys.argv) == 2:
        fstab=sys.argv[1]
    sys.exit(CheckSwap().main(fstab))
