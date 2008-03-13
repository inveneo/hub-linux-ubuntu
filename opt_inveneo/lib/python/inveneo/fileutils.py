#!/usr/bin/env python     
# -*- coding: utf-8 -*-

from __future__ import with_statement
import StringIO
import mmap
import sys
import os
import re

PROP_PARSER=re.compile("^\s*(?!#)(\S+)\s*=\s*[\"\']?(.+?)[\"\']?$")
            
class ConfigFileDict(object):
    def __init__(self,filepath):
        self.config_file=os.path.abspath(filepath)
        self.dict={}
        if os.path.isfile(self.config_file):
            with open(self.config_file,'r') as f:
                for line in f.readlines():
                    m=PROP_PARSER.match(line)
                    if m:
                        key,value=m.groups()
                        self.dict[key]=value

    def save_config(self):
        with open(self.config_file,'w') as f:
            for key,value in self.dict.items():
                f.write("%s=\"%s\"\n" % (str(key),str(value)))

	
    def get_as_int(self,key, default=-1):
        val=int(default)
        if key in self.dict:
            try:
                val=int(self.dict[key])
            except:
                val=int(default)
        return val

    def get_as_str(self,key, default=""):
        val=str(default)
        if key in self.dict:
            try:
                val=str(self.dict[key])
            except:
                val=str(default)
        return val

    def set_as_str(self,key,val):
        self.dict[key]=str(val)                
    

def replace_in_file(t, r, fn):
    """ Args are: token, replacement, file """
    
    f=open(fn,'r+')
    
    if not (isinstance(f,file) and isinstance(t, str) and isinstance(r,str)):
        raise TypeError 
    
    fmap=mmap.mmap(f.fileno(),0,mmap.ACCESS_READ)
    filesize=fmap.size()
    buf=StringIO.StringIO()
    
    toklen=len(t)
    
    start=0
    tokindex=fmap.find(t,start)
    while tokindex != -1:
        # we found a token, copy everything from start to token, then replacement
        buf.write(fmap[start:tokindex]+r)
        
        # now skip past length of token
        start=tokindex+toklen
        tokindex=fmap.find(t,start)
        
    # now make sure we put what's left into the buffer
    try:
        buf.write(fmap[start:])
    except:
        pass 
    
    fmap.close()
    f.close()
    
    f=open(fn,'w')
    f.write(buf.getvalue())
    f.close()
    buf.close()
    

# a main for testing
if __name__ == "__main__":
    # sanitize PATH                                                                                                             
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    if len(sys.argv) != 4:
        print "Usage: fileutils.py token replacement filename"
        sys.exit(1)
        
    replace_in_file(sys.argv[1],sys.argv[2],sys.argv[3])


        
