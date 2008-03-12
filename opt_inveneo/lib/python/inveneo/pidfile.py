#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pidfile.py - Library to handle process management via pid files in /var/run

Copyright (c) 2008 Inveneo, inc. All rights reserved.
"""

from __future__ import with_statement
import sys
import os
import traceback
import signal
sys.path.append('/opt/inveneo/lib/python')

PID_DIR=os.path.join('/','var','run')

class PIDFile(object):
    def __init__(self, pname):
        self.pname=pname
        self.my_pid=os.getpid()
        self.pid_file=os.path.join(PID_DIR,self.pname)+".pid"
        self.pid_file_pid=-1
        
	# See if there is a PID file
        if os.path.isfile(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    self.pid_file_pid=int(f.readline())
            except:
                traceback.print_exc(file=sys.stderr)
                raise Exception("pid file '%s' exists but cannot be read" % self.pid_file)
            else:
                if not self.pid_file_pid > 0:
                    raise Exception("PID file value bogus: %s" % self.pid_file_pid)
        
        # no PID file so create one for us
        else:
            try:
                with open(self.pid_file, 'w') as f:
                    f.write(str(self.my_pid)+"\n")
                self.pid_file_pid=self.my_pid
            except:
                traceback.print_exc(file=sys.stderr)
                raise Exception("Was unable to write pid file: %s" % self.pid_file)
                
    def pid_is_this_process(self):
        return self.pid_file_pid == self.my_pid
    
    def remove_pid_file(self):
        """Blows away PID file regardless of whether the PID matches this process.
        Does not kill process.
        Allows any file excpetions to bubble up."""

        os.remove(self.pid_file)
    
    def kill_process_and_remove_pid_file(self):
        success=True

        if self.is_running():
            try:
                os.kill(self.pid_file_pid, signal.SIGKILL)
            except:
                success=False

        if success:
            self.remove_pid_file()

        return success

    def is_running(self):
        return str(self.get_pid()) in os.listdir('/proc')

    def get_pid(self):
        return self.pid_file_pid

    def get_pid_file_name(self):
        return self.pid_file

    

# a main for testing
if __name__ == "__main__":
    # sanitize PATH                                                                                                             
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    if len(sys.argv) != 2:
        print "Usage: pidfile.py pid_file_name"
        sys.exit(1)
        
    p=PIDFile(sys.argv[1])
    sys.stdout.write("PID file: %s, PID: %d\n" % (p.get_pid_file_name(), p.get_pid()))

    if not p.pid_is_this_process():
        if not p.kill_process_and_remove_pid_file(): p.remove_pidfile()
        p=PIDFile('foo')
        sys.stdout.write("NOW PID file: %s, PID: %d\n" % (p.get_pid_file_name(), p.get_pid()))
    while True:
        pass
    



    
