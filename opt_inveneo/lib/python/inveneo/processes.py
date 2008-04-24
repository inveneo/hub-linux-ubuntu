#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
processes.py - Class that encapsulates current system process list.

This class holds a structured representation of a snapshot of
the system process list.

Copyright (c) 2008 Inveneo, inc. All rights reserved.
"""

import string
from subprocess import Popen, PIPE

class ProcSnap(object):
    """A snapshot of system processes.

    Holds information on the relationship of processes."""
    
    def __init__(self):
        """Snapshot system process list."""
        cmdlist = ['/bin/ps', '-eo', 'pid,ppid,args']
        (sout, serr) = Popen(cmdlist, stdout=PIPE, stderr=PIPE).communicate()
        if serr:
            raise Exception(serr)
        self.procs = {}
        for line in sout.split('\n')[1:-1]:
            list = line.split()
            pid = int(list[0])
            ppid = int(list[1])
            cmd = list[2]
            args = string.join(list[3:], ' ')
            self.procs[pid] = (ppid, cmd, args)

    def toplevel(self):
        """Return list of top level process info."""
        retval = []
        pidlist = self.procs.keys()
        pidlist.sort()
        for pid in pidlist:
            (ppid, cmd, args) = self.procs[pid]
            if ppid == 1:
                retval.append([pid, cmd, args])
        return retval

    def __str__(self):
        """Return entire data structure as a string."""
        lines = []
        pidlist = self.procs.keys()
        pidlist.sort()
        for pid in pidlist:
            (ppid, cmd, args) = self.procs[pid]
            lines.append('%d %d %s %s' % (pid, ppid, cmd, args))
        return string.join(lines, '\n')

if __name__ == '__main__':
    """Exercise the class."""
    o = ProcSnap()

    print "===== Top Dogs ====="
    for (pid, cmd, args) in o.toplevel():
        print '%d %s %s' % (pid, cmd, args)

    print "===== ALL OF IT ====="
    print str(o)

