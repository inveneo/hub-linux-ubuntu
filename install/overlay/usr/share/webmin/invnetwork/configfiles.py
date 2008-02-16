#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
configfiles.py - classes that encapsulate various system config files

Copyright (c) 2007 Inveneo, inc. All rights reserved.
"""

import sys, traceback, string, os
sys.path.append('/opt/inveneo/lib/python')

class ConfigFileBase(object):
    """operations and data present in all config file managers"""

    def __init__(self, filepath, uses_line_continuation = False):
        """initialize self from config file: simply read into memory"""
        self.filepath = filepath
        self.lines = []

        fin = open(filepath, 'r')
        line_buffer = ''
        for line in fin.readlines():
            # see if this line is "to be continued..."
            rstripped_line = line.rstrip()
            if uses_line_continuation and rstripped_line.endswith('\\'):
                line_buffer += rstripped_line[:-1] + ' '
            else:
                line_buffer += line
                self.lines.append(line_buffer)
                line_buffer = ''
        fin.close()

    def write(self, makeBackup = True):
        """rewrite the config file, perhaps making a backup of the old one"""
        if makeBackup:
            bakfilepath = self.filepath + '.bak'
            try: os.remove(bakfilepath)
            except: pass
            os.rename(self.filepath, bakfilepath)
        else:
            try: os.remove(self.filepath)
            except: pass
        fout = open(self.filepath, 'w')
        fout.writelines(self.lines)
        fout.close()

class EtcWvdialConf(ConfigFileBase):
    """wvdial configuration"""

    def __init__(self):
        """initialize self from config file, parsing out metadata"""
        ConfigFileBase.__init__(self, '/etc/wvdial.conf.test')
        self.metadata = {}

        for line in self.lines:
            (key, value) = self._parse_line(line)
            if key in ['modem', 'phone', 'username', 'password', 'baud', \
                    'idle seconds', 'init1', 'init2']:
                self.metadata[key] = value

    def _parse_line(self, line):
        """parse out the interesting bits of one line"""
        eq = line.find('=')
        if eq > 0:
            key = line[0:eq].strip().lower()
            value = line[eq+1:].strip()
            return (key, value)
        return (None, None)

    def _update_lines(self):
        """return original list of lines updated by metadata"""
        newlines = []
        found_keys = set()

        # alter existing lines that have metadata overrides
        for line in self.lines:
            (key, value) = self._parse_line(line)
            if self.metadata.has_key(key):
                line = "%s = %s\n" % (key, self.metadata[key])
                found_keys.add(key)
            newlines.append(line)

        # add lines for metadata not yet existing in file
        meta_keys = set(self.metadata.keys())
        for key in meta_keys.difference(found_keys):
            newlines.append("%s = %s\n" % (key, self.metadata[key]))
        return newlines

    def __str__(self):
        """return entire config file as string, modified by parsed content"""
        return string.join(self._update_lines(), '')

    def write(self, makeBackup = True):
        """rewrite the config file, perhaps making a backup of the old one"""
        self.lines = self._update_lines()
        ConfigFileBase.write(makeBackup)

class EtcDhcp3DhcpConf(ConfigFileBase):
    """DHCP configuration"""

    class SubnetSection(object):
        """helper class that encapsulates one subnet"""

        # static methods
        def begins(line):
            """answer whether this line begins a new section of interest"""
            tokens = line.split()
            return tokens and tokens[0].lower() == 'subnet'
        begins = staticmethod(begins)

        def ends(line):
            """answer whether this line ends a section of interest"""
            tokens = line.split()
            return '}' in tokens
        ends = staticmethod(ends)

        def get_key(line):
            """return subnet parsed from first line of section"""
            tokens = line.split()
            return tokens[1]
        get_key = staticmethod(get_key)

        # instance methods
        def __init__(self, line):
            """initialize from first line of section"""
            self.subnet = None
            self.netmask = None
            self.start_ip = None
            self.end_ip = None
            self.options = {}

            self.add_line(line)

        def add_line(self, line):
            """add line of file to section, return False on last line"""
            tokens = line.split()
            if tokens:
                keyword = tokens[0].lower()
                if keyword == 'subnet':
                    self.subnet = tokens[1]
                    self.netmask = tokens[3]
                elif keyword == 'range':
                    self.start_ip = tokens[1]
                    self.end_ip = tokens[2].strip(';')
                elif keyword == 'option':
                    key = tokens[1]
                    value = tokens[2].strip(';')
                    self.options[key] = value
                if '}' in set(tokens):
                    return False
            return True

        def lines(self):
            """return list of config lines generated by this section"""
            lines = []
            lines.append('subnet %s netmask %s {\n' % \
                    (self.subnet, self.netmask))
            if self.start_ip and self.end_ip:
                lines.append('\trange %s %s;\n' % (self.start_ip, self.end_ip))
            for key, value in self.options.iteritems():
                lines.append('\toption %s %s;\n' % (key, value))
            lines.append('}\n')
            return lines

        def __str__(self):
            """return single string representation of self"""
            return string.join(self.lines(), '')

    def __init__(self):
        """initialize self from config file, parsing out interesting content"""
        ConfigFileBase.__init__(self, '/etc/dhcp3/dhcpd.conf')
        self.subnets = {}

        section = None
        for line in self.lines:
            if section:
                if not section.add_line(line):
                    self.subnets[section.subnet] = section
                    section = None
            elif self.SubnetSection.begins(line):
                section = self.SubnetSection(line)
        if section:
            section.add_line(line)
            self.subnets[section.subnet] = section

    def _update_lines(self):
        """return copy of stored lines updated by metadata"""
        newlines = []
        found_keys = set()

        # replace sections of interest with metadata (else remove)
        subnet_name = None
        for line in self.lines:
            if subnet_name:
                # we are inside a section: are we done yet?
                if self.SubnetSection.ends(line):
                    # insert metadata instead, if there is any
                    if self.subnets.has_key(subnet_name):
                        newlines.extend(self.subnets[subnet_name].lines())
                        found_keys.add(subnet_name)
                    subnet_name = None
            else:
                # not inside a section: is this the start of one?
                if self.SubnetSection.begins(line):
                    # yes: pluck out its name
                    subnet_name = self.SubnetSection.get_key(line)
                else:
                    # nope: just some random stuff to copy through
                    newlines.append(line)

        # add lines for metadata not yet existing in stored lines
        keys = set(self.subnets.keys())
        for subnet_name in keys.difference(found_keys):
            newlines.extend(self.subnets[subnet_name].lines())
        return newlines

    def __str__(self):
        """return entire config file as string, modified by parsed content"""
        return string.join(self._update_lines(), '')

    def write(self, makeBackup = True):
        """rewrite the config file, perhaps making a backup of the old one"""
        self.lines = self._update_lines()
        ConfigFileBase.write(makeBackup)

class EtcNetworkInterfaces(ConfigFileBase):
    """network interfaces definitions"""

    class InterfaceStanza(object):
        """helper class that encapsulates one interface"""

        # static methods
        def begins(line):
            """answer whether this line begins a new stanza"""
            tokens = line.split()
            return tokens and tokens[0].lower() == 'iface'
        begins = staticmethod(begins)

        def ends(line):
            """answer whether this line ends a stanza"""
            tokens = line.split()
            return tokens and ( \
                    tokens[0].lower() in ['iface', 'mapping', 'auto'] or \
                    tokens[0].lower().startswith('allow-'))
        ends = staticmethod(ends)

        def get_key(line):
            """return interface parsed from first line of iface stanza"""
            tokens = line.split()
            return tokens[1]
        get_key = staticmethod(get_key)

        # instance methods
        def __init__(self, line):
            """initialize from first line of stanza"""
            self.iface = None
            self.method = None
            self.address = None
            self.netmask = None
            self.gateway = None
            self.extras = []

            self.add_line(line)

        def add_line(self, line):
            """add line of file to stanza"""
            tokens = line.split()
            if tokens:
                keyword = tokens[0].lower()
                if keyword == 'iface':
                    self.iface = tokens[1]
                    self.method = tokens[3]
                elif keyword == 'address':
                    self.address = tokens[1]
                elif keyword == 'netmask':
                    self.netmask = tokens[1]
                elif keyword == 'gateway':
                    self.gateway = tokens[1]
                else:
                    self.extras.append(line)
            else:
                self.extras.append(line)

        def lines(self):
            """return list of config lines generated by this stanza"""
            lines = []
            lines.append('iface %s inet %s\n' % (self.iface, self.method))
            if self.address:
                lines.append('\taddress %s\n' % (self.address))
            if self.netmask:
                lines.append('\tnetmask %s\n' % (self.netmask))
            if self.gateway:
                lines.append('\tgateway %s\n' % (self.gateway))
            lines.append(string.join(self.extras, ''))
            return lines

        def __str__(self):
            """return single string representation of self"""
            return string.join(self.lines(), '')

    def __init__(self):
        """initialize self from config file, parsing out interesting content"""
        ConfigFileBase.__init__(self, '/etc/network/interfaces', True)
        self.autoset = set()
        self.ifaces = {}

        stanza = None
        for line in self.lines:
            if stanza:
                if not self.InterfaceStanza.ends(line):
                    stanza.add_line(line)
                    continue
                else:
                    self.ifaces[stanza.iface] = stanza
                    stanza = None
            if self.InterfaceStanza.begins(line):
                stanza = self.InterfaceStanza(line)
            else:
                tokens = line.split()
                if tokens and tokens[0].lower() == 'auto':
                    self.autoset.update(tokens[1:])
        if stanza:
            self.ifaces[stanza.iface] = stanza

    def _update_lines(self):
        """return copy of stored lines updated by metadata"""
        newlines = []
        found_keys = set()
        found_auto = set()

        # replace stanzas of interest with metadata (else remove them)
        iface_name = None
        for line in self.lines:
            if iface_name:
                # we are inside an interface stanza: are we done yet?
                if self.InterfaceStanza.ends(line):
                    # insert metadata instead, if there is any
                    if self.ifaces.has_key(iface_name):
                        newlines.extend(self.ifaces[iface_name].lines())
                        found_keys.add(iface_name)
                    iface_name = None
            if not iface_name:
                # not inside interface stanza: is this the start of one?
                if self.InterfaceStanza.begins(line):
                    # yes: pluck out its name
                    iface_name = self.InterfaceStanza.get_key(line)
                else:
                    tokens = line.split()
                    if tokens and tokens[0].lower() == 'auto':
                        # this is an auto stanza
                        newline = 'auto'
                        for iface in tokens[1:]:
                            if iface in self.autoset:
                                newline += ' ' + iface
                                found_auto.add(iface)
                        newlines.append(newline + '\n')
                    else:
                        # nope: just some random stuff to copy through
                        newlines.append(line)

        # add lines for metadata not yet existing in stored lines
        new_autos = self.autoset.difference(found_auto)
        if len(new_autos):
            newline = 'auto'
            for iface in new_autos:
                newline += ' ' + iface
            newlines.append(newline + '\n')
        keys = set(self.ifaces.keys())
        for iface_name in keys.difference(found_keys):
            newlines.extend(self.ifaces[iface_name].lines())
        return newlines

    def __str__(self):
        """return entire config file as string, modified by parsed content"""
        return string.join(self._update_lines(), '')

    def write(self, makeBackup = True):
        """rewrite the config file, perhaps making a backup of the old one"""
        self.lines = self._update_lines()
        ConfigFileBase.write(makeBackup)

def main():
    """test these classes"""

    print "==================================================="
    print "Parsing /etc/wvdial.conf"
    print "==================================================="
    o = EtcWvdialConf()
    print "* Metadata =", o.metadata
    print "* File contents:\n----------------------\n%s" % str(o)

    print "==================================================="
    print "Parsing /etc/dhcp3/dhcp.conf"
    print "==================================================="
    o = EtcDhcp3DhcpConf()
    print "* Subnets =", o.subnets
    print "* File contents:\n----------------------\n%s" % str(o)

    print "==================================================="
    print "Parsing /etc/network/interfaces"
    print "==================================================="
    o = EtcNetworkInterfaces()
    print "* Auto Start =", o.autoset
    print "* Interfaces =", o.ifaces
    print "* File contents:\n----------------------\n%s" % str(o)

if __name__ == '__main__':
    main()

