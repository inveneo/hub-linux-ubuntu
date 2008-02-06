#!/usr/bin/env python

# netfiles.py - classes that understand various network config files

import sys, traceback, string

class ConfigFileBase(object):
    """base class for rest of specific config file classes"""

    def __init__(self, filepath):
        """initialize self from config file"""
        fin = open(filepath, 'r')
        self.lines = fin.readlines()
        fin.close()

    def __str__(self):
        """return entire config file as string"""
        return string.join(self.lines, '')

class EtcNetworkInterfaces(ConfigFileBase):

    FILEPATH = '/etc/network/interfaces'
    autoset = set()
    ifaces = {}

    def __init__(self):
        ConfigFileBase.__init__(self, self.FILEPATH)
        for line in self.lines:
            tokens = line.strip().split()
            if tokens:
                if tokens[0] == 'auto':
                    self.autoset.update(tokens[1:])
                elif tokens[0] == 'iface':
                    self.iface = {}
                    name = tokens[1]
                    self.ifaces[name] = self.iface
                    self.iface['method'] = tokens[3]
                elif tokens[0] in ['address', 'netmask', 'gateway']:
                    self.iface[tokens[0]] = tokens[1]

class EtcWvdialConf(ConfigFileBase):

    FILEPATH = '/etc/wvdial.conf'
    pairs = {}

    def __init__(self):
        ConfigFileBase.__init__(self, self.FILEPATH)
        for line in self.lines:
            eq = line.find('=')
            if eq > 0:
                key = line[0:eq].strip().lower()
                value = line[eq+1:].strip()
                if key in ['modem', 'phone', 'username', 'password', \
                        'baud', 'idle seconds', 'init1', 'init2']:
                    self.pairs[key] = value

class EtcDhcp3DhcpConf(ConfigFileBase):

    FILEPATH = '/etc/dhcp3/dhcpd.conf'
    pairs = {}

    def __init__(self):
        ConfigFileBase.__init__(self, self.FILEPATH)
        for line in self.lines:
            tokens = line.strip().split()
            if tokens:
                if tokens[0] == 'range':
                    start_ip = tokens[1]
                    end_ip = tokens[2].strip(';')
                    self.pairs['dhcp_range_start'] = start_ip.split('.')[3]
                    self.pairs['dhcp_range_end'] = end_ip.split('.')[3]

def main():
    o = EtcNetworkInterfaces()
    print o
    print "Auto Start =", o.autoset
    print "Interfaces =", o.ifaces
    print "==================================================="
    o = EtcWvdialConf()
    print o
    print "Pairs =", o.pairs
    print "==================================================="
    o = EtcDhcp3DhcpConf()
    print o
    print "Pairs =", o.pairs

if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc(20, sys.stdout)

