#!/usr/bin/env python     
# -*- coding: utf-8 -*-

import StringIO
import mmap
import sys
import os

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
    print "start: "+str(filesize)+" extent: "+str((filesize-start+1))+"\n"+fmap[start:]
    buf.write(fmap[start:])
    
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


        
