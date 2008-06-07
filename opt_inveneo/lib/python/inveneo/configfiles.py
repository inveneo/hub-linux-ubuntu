#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
configfiles.py - Classes that manipulate specific system config files.

These classes read an assortment of configuration files and present
the "interesting" sections of those files as attributes and instances
of inner classes, so a user can easily twiddle values and add or
remove whole sections without knowing anything about the format of
the file.  The classes rewrite the files, trying to preserve as much
of their integrity (empty lines, comments, "uninteresting" sections)
as possible.

Copyright (c) 2008 Inveneo, inc. All rights reserved.
"""

import sys, traceback, string, os
from IPy import IP

class ConfigFileBase(object):
    """Operations and data present in all config file managers.
    
    The managers for specific config files should be derived from this
    base class.  The base class provides their common functionality,
    namely, reading the config file into memory and writing the config
    file back to disk (with an option to create a backup)."""

    def __init__(self, filepath, uses_line_continuation = False):
        """Initialize self from config file.
        
        Simply read the file into memory as a list of lines with
        newlines intact.  The optional flag allows for combining
        'continuation lines'."""

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
        """Rewrite the config file.
        
        If flag is set, make a backup of the old one."""

        if makeBackup:
            bakfilepath = self.filepath + '~'
            try: os.remove(bakfilepath)
            except: pass
            os.rename(self.filepath, bakfilepath)
        else:
            try: os.remove(self.filepath)
            except: pass
        fout = open(self.filepath, 'w')
        fout.writelines(self.lines)
        fout.close()

class EtcHostname(ConfigFileBase):
    """Hostname
    
    This file is trivial: a single value."""

    def __init__(self):
        """Initialize self from config file, parsing out metadata."""
        ConfigFileBase.__init__(self, '/etc/hostname')
        self.hostname = None
        for line in self.lines:
            hostname = self._parse_line(line)
            if hostname:
                self.hostname = hostname

    def _parse_line(self, line):
        """Parse out the interesting bits of one line.
        
        Returns the first word on the line, else None."""
        if not line.startswith('#'):
            list = line.split()
            if len(list) == 1:
                return list[0]
        return None

    def _update_lines(self):
        """Return original list of lines updated by current metadata.
        
        Returns a list of lines that probably have newlines at the end."""
        newlines = []
        for line in self.lines:
            hostname = self._parse_line(line)
            if hostname:
                newlines.append("%s\n" % self.hostname)
            else:
                newlines.append(line)
        return newlines

    def __str__(self):
        """Return entire config file as string, modified by current metadata."""
        return string.join(self._update_lines(), '')

    def write(self, makeBackup = True):
        """Rewrite the config file, perhaps making a backup of the old one."""
        self.lines = self._update_lines()
        ConfigFileBase.write(self, makeBackup)

class EtcResolvConf(ConfigFileBase):
    """DNS configuration.
    
    This file is easy: mostly just key/values."""

    def __init__(self):
        """Initialize self from config file, parsing out metadata."""
        ConfigFileBase.__init__(self, '/etc/resolv.conf')
        self.nameservers = []

        for line in self.lines:
            (key, value) = self._parse_line(line)
            if key == 'nameserver':
                self.nameservers.append(value)

    def _parse_line(self, line):
        """Parse out the interesting bits of one line.
        
        Returns a (key, value) tuple, else (None, None)."""
        list = line.split()
        if len(list) > 1:
            key = list[0].lower()
            value = list[1]
            return (key, value)
        return (None, None)

    def _update_lines(self):
        """Return original list of lines updated by current metadata.
        
        Returns a list of lines that probably have newlines at the end."""
        newlines = []

        # write out non-nameserver lines first
        for line in self.lines:
            (key, value) = self._parse_line(line)
            if key != 'nameserver':
                newlines.append(line)

        # add nameservers at the end
        for value in self.nameservers:
            newlines.append("nameserver %s\n" % value)
        return newlines

    def __str__(self):
        """Return entire config file as string, modified by current metadata."""
        return string.join(self._update_lines(), '')

    def write(self, makeBackup = True):
        """Rewrite the config file, perhaps making a backup of the old one."""
        self.lines = self._update_lines()
        ConfigFileBase.write(self, makeBackup)

class EtcHosts(ConfigFileBase):
    """The static table lookup for host names.
    
    This file is lines of: IP_address canonical_hostname [aliases...]
    Comments begin with # at any point in line.
    There are other rules for hostnames, which we ignore at present."""

    def __init__(self):
        """Initialize self from config file, parsing out metadata."""
        ConfigFileBase.__init__(self, '/etc/hosts')
        self.ips = {}

        for line in self.lines:
            (ip, names) = self._parse_line(line)
            if ip:
                try:
                    ipobj = IP(ip)
                except:
                    continue # bad IP: ignore
                self.ips[ip] = names

    def _parse_line(self, line):
        """Parse out the interesting bits of one line.
        
        Returns (ip, names) tuple, where names is a list of aliases,
        else (None, None)."""
        list = line.split('#')
        meat = list[0].split()
        if len(meat) > 1:
            ip = meat[0]
            names = meat[1:]
            return (ip, names)
        return (None, None)

    def _update_lines(self):
        """Return original list of lines updated by current metadata.
        
        Returns a list of lines that probably have newlines at the end."""
        newlines = []
        found_ips = set()

        # write out non-nameserver lines first
        for line in self.lines:
            (ip, names) = self._parse_line(line)
            if ip:
                try:
                    ipobj = IP(ip)
                except:
                    continue # bad IP: ignore
                if ip in self.ips:
                    line = "%s %s\n" % (ip, string.join(self.ips[ip], ' '))
                    found_ips.add(ip)
                    newlines.append(line)
            else:
                newlines.append(line)

        # add lines for ips not yet existing in file
        all_ips = set(self.ips.keys())
        for ip in all_ips.difference(found_ips):
            newlines.append("%s %s\n" % (ip, string.join(self.ips[ip], ' ')))
        return newlines

    def __str__(self):
        """Return entire config file as string, modified by current metadata."""
        return string.join(self._update_lines(), '')

    def write(self, makeBackup = True):
        """Rewrite the config file, perhaps making a backup of the old one."""
        self.lines = self._update_lines()
        ConfigFileBase.write(self, makeBackup)

class EtcWvdialConf(ConfigFileBase):
    """Wvdial configuration.
    
    This file is easy: mostly just key/value pairs.
    We only store the ones we are interested in."""

    def __init__(self):
        """Initialize self from config file, parsing out metadata."""
        ConfigFileBase.__init__(self, '/etc/wvdial.conf')
        self.metadata = {}

        for line in self.lines:
            (key, value) = self._parse_line(line)
            if key in ['modem', 'phone', 'username', 'password', 'baud', \
                    'idle seconds', 'init1', 'init2', 'carrier check']:
                self.metadata[key] = value

    def _parse_line(self, line):
        """Parse out the interesting bits of one line.
        
        Returns a (key, value) tuple, else (None, None)."""
        eq = line.find('=')
        if eq > 0:
            key = line[0:eq].strip().lower()
            value = line[eq+1:].strip()
            return (key, value)
        return (None, None)

    def _update_lines(self):
        """Return original list of lines updated by current metadata.
        
        Returns a list of lines that probably have newlines at the end."""
        newlines = []
        found_keys = set()

        # alter existing lines that have metadata overrides
        for line in self.lines:
            (key, value) = self._parse_line(line)
            if key in self.metadata:
                line = "%s = %s\n" % (key, self.metadata[key])
                found_keys.add(key)
            newlines.append(line)

        # add lines for metadata not yet existing in file
        meta_keys = set(self.metadata.keys())
        for key in meta_keys.difference(found_keys):
            newlines.append("%s = %s\n" % (key, self.metadata[key]))
        return newlines

    def __str__(self):
        """Return entire config file as string, modified by current metadata."""
        return string.join(self._update_lines(), '')

    def write(self, makeBackup = True):
        """Rewrite the config file, perhaps making a backup of the old one."""
        self.lines = self._update_lines()
        ConfigFileBase.write(self, makeBackup)

class EtcPppPeersDod(ConfigFileBase):
    """Dial On Demand configuration.
    
    This file is mostly just keywords or key/value pairs."""

    def __init__(self):
        """Initialize self from config file, parsing out metadata."""
        ConfigFileBase.__init__(self, '/etc/ppp/peers/dod')
        self.metadata = {}
        for line in self.lines:
            (key, value) = self._parse_line(line)
            if key:
                self.metadata[key] = value

    def _parse_line(self, line):
        """Parse out the interesting bits of one line.
        
        Returns (key, value) or (key, None) or (None, None).
        See 'man 8 pppd' for syntax of the options file, and to see
        how badly we are ignoring the format here."""
        # XXX we really need to pay attention to double quotes, comments,
        # and backslashes!
        if len(line) == 0: return (None, None)
        space = line.find(' ')
        if space > 0:
            key = line[0:space].strip()
            value = line[space+1:].strip()
            return (key, value)
        # look for two special-case pain-in-the-butt values
        key = line.strip()
        if key.startswith('/'):
            # XXX (somewhat bogus) assumption that we've found modem name
            return ('ttyname', key)
        elif key[0].isdigit():
            # XXX (somewhat bogus) assumption that we've found baud rate
            return ('speed', key)
        return (key, None)

    def _update_lines(self):
        """Return original list of lines updated by current metadata.
        
        Returns a list of lines that probably have newlines at the end."""
        newlines = []
        found_keys = set()

        # alter existing lines that have metadata overrides
        for line in self.lines:
            (key, value) = self._parse_line(line)
            if key and (key in self.metadata):
                value = self.metadata[key]
                if value:
                    if (key == 'ttyname') or (key == 'speed'):
                        line = "%s\n" % value
                    else:
                        line = "%s %s\n" % (key, value)
                else:
                    line = "%s\n" % key
                found_keys.add(key)
            newlines.append(line)

        # add lines for metadata not yet existing in file
        meta_keys = set(self.metadata.keys())
        for key in meta_keys.difference(found_keys):
            value = self.metadata[key]
            if value:
                if (key == 'ttyname') or (key == 'speed'):
                    newlines.append("%s\n" % value)
                else:
                    newlines.append("%s %s\n" % (key, value))
            else:
                newlines.append("%s\n" % key)
        return newlines

    def __str__(self):
        """Return entire config file as string, modified by current metadata."""
        return string.join(self._update_lines(), '')

    def write(self, makeBackup = True):
        """Rewrite the config file, perhaps making a backup of the old one."""
        self.lines = self._update_lines()
        ConfigFileBase.write(self, makeBackup)

class EtcDhcp3DhclientConf(ConfigFileBase):
    """DHCP Client configuration."""

    def __init__(self):
        """Initialize self from config file, parsing out interesting content."""
        ConfigFileBase.__init__(self, '/etc/dhcp3/dhclient.conf')
        self.nameservers = []
        for line in self.lines:
            namelist = self._parse_line(line)
            if namelist and len(namelist) > 0:
                self.nameservers += namelist

    def _parse_line(self, line):
        """Parse out the interesting bits of one line.
        
        Returns list of nameservers, or None if wrong line."""
        line = line.strip().strip(';')
        fields = line.split(' ', 2)
        if (len(fields) < 2) or \
           (fields[0].lower() != 'append') or \
           (fields[1].lower() != 'domain-name-servers'):
               return None
        result = []
        if len(fields) > 2:
            for address in fields[2].split(','):
                result.append(address.strip())
        return result

    def _update_lines(self):
        """Return original list of lines updated by current metadata."""
        newlines = []
        for line in self.lines:
            namelist = self._parse_line(line)
            if namelist == None:
                newlines.append(line)
            elif self.nameservers:
                line = 'append domain-name-servers %s;\n' % \
                        string.join(self.nameservers, ',')
                newlines.append(line)
        return newlines

    def __str__(self):
        """Return entire config file as string, modified by current metadata."""
        return string.join(self._update_lines(), '')

    def write(self, makeBackup = True):
        """Rewrite the config file, perhaps making a backup of the old one."""
        self.lines = self._update_lines()
        ConfigFileBase.write(self, makeBackup)

class EtcDhcp3DhcpConf(ConfigFileBase):
    """DHCP Server configuration.
    
    The metadata is a dictionary of subnet objects."""

    class SubnetSection(object):
        """Helper class that encapsulates one subnet.
        
        Attributes include IP objects (subnet, netmask, start and end of
        DHCP range), and other lines found."""

        # static methods
        def begins(line):
            """Answer whether this line begins a new section of interest."""
            tokens = line.split()
            return tokens and tokens[0].lower() == 'subnet'
        begins = staticmethod(begins)

        def ends(line):
            """Answer whether this line ends a section of interest."""
            tokens = line.split()
            return '}' in tokens
        ends = staticmethod(ends)

        def get_key(line):
            """Return subnet id parsed from first line of section."""
            tokens = line.split()
            return tokens[1]
        get_key = staticmethod(get_key)

        # instance methods
        def __init__(self, line):
            """Initialize from first line of section."""
            self.subnet = None
            self.netmask = None
            self.start_ip = None
            self.end_ip = None
            self.options = {}

            self.add_line(line)

        def add_line(self, line):
            """Add line of file to section, return False on last line."""
            tokens = line.split()
            if tokens:
                keyword = tokens[0].lower()
                if keyword == 'subnet':
                    self.subnet = IP(tokens[1])
                    self.netmask = IP(tokens[3])
                elif keyword == 'range':
                    self.start_ip = IP(tokens[1])
                    self.end_ip = IP(tokens[2].strip(';'))
                elif keyword == 'option':
                    key = tokens[1]
                    value = tokens[2].strip(';')
                    self.options[key] = value
                if '}' in set(tokens):
                    return False
            return True

        def lines(self):
            """Return list of config lines generated by this section."""
            lines = []
            lines.append('subnet %s netmask %s {\n' % \
                    (self.subnet.strNormal(), self.netmask.strNormal()))
            if self.start_ip and self.end_ip:
                lines.append('\trange %s %s;\n' % \
                        (self.start_ip.strNormal(), self.end_ip.strNormal()))
            for key, value in self.options.iteritems():
                lines.append('\toption %s %s;\n' % (key, value))
            lines.append('}\n')
            return lines

        def __str__(self):
            """Return single string representation of self."""
            return string.join(self.lines(), '')

    def __init__(self):
        """Initialize self from config file, parsing out interesting content."""
        ConfigFileBase.__init__(self, '/etc/dhcp3/dhcpd.conf')
        self.subnets = {}

        section = None
        for line in self.lines:
            if section:
                if not section.add_line(line):
                    self.subnets[section.subnet.strNormal()] = section
                    section = None
            elif self.SubnetSection.begins(line):
                section = self.SubnetSection(line)
        if section:
            section.add_line(line)
            self.subnets[section.subnet.strNormal()] = section

    def _update_lines(self):
        """Return copy of stored lines updated by current metadata."""
        newlines = []
        found_keys = set()

        # replace sections of interest with metadata (else remove)
        subnet_name = None
        for line in self.lines:
            if subnet_name:
                # we are inside a section: are we done yet?
                if self.SubnetSection.ends(line):
                    # insert metadata instead, if there is any
                    if subnet_name in self.subnets:
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

    def add_subnet(self, network, netmask):
        """Create a new network segment with minimal info."""
        line = "subnet %s netmask %s {\n" % (network, netmask)
        section = self.SubnetSection(line)
        self.subnets[section.subnet.strNormal()] = section
        return section

    def __str__(self):
        """Return entire config file as string, modified by current metadata."""
        return string.join(self._update_lines(), '')

    def write(self, makeBackup = True):
        """Rewrite the config file, perhaps making a backup of the old one."""
        self.lines = self._update_lines()
        ConfigFileBase.write(self, makeBackup)

class EtcNetworkInterfaces(ConfigFileBase):
    """Represents network interfaces definitions.
    
    Metadata is a dictionary of interface objects, and the set of
    interfaces to be auto-up'd."""

    class InterfaceStanza(object):
        """Helper class that encapsulates one interface.
        
        Attributes include interface name, method of obtaining address,
        IP objects (static address, static netmask, static gateway),
        and list of other lines in the stanza."""

        # static methods
        def begins(line):
            """Answer whether this line begins a new stanza."""
            tokens = line.split()
            return tokens and tokens[0].lower() == 'iface'
        begins = staticmethod(begins)

        def ends(line):
            """Answer whether this line ends a stanza."""
            tokens = line.split()
            return tokens and ( \
                    tokens[0].lower() in ['iface', 'mapping', 'auto'] or \
                    tokens[0].lower().startswith('allow-'))
        ends = staticmethod(ends)

        def get_key(line):
            """Return interface parsed from first line of iface stanza."""
            tokens = line.split()
            return tokens[1]
        get_key = staticmethod(get_key)

        # instance methods
        def __init__(self, line):
            """Initialize from first line of stanza."""
            self.iface = None
            self.method = None
            self.address = None
            self.netmask = None
            self.gateway = None
            self.extras = []

            self.add_line(line)

        def add_line(self, line):
            """Add line of file to stanza."""
            tokens = line.split()
            if tokens:
                keyword = tokens[0].lower()
                if keyword == 'iface':
                    self.iface = tokens[1]
                    self.method = tokens[3]
                elif keyword == 'address':
                    self.address = IP(tokens[1])
                elif keyword == 'netmask':
                    self.netmask = IP(tokens[1])
                elif keyword == 'gateway':
                    self.gateway = IP(tokens[1])
                else:
                    self.extras.append(line)
            else:
                self.extras.append(line)

        def lines(self):
            """Return list of config lines generated by this stanza."""
            lines = []
            lines.append('iface %s inet %s\n' % (self.iface, self.method))
            if self.address:
                lines.append('\taddress %s\n' % (self.address.strNormal()))
            if self.netmask:
                lines.append('\tnetmask %s\n' % (self.netmask.strNormal()))
            if self.gateway:
                lines.append('\tgateway %s\n' % (self.gateway.strNormal()))
            lines.append(string.join(self.extras, ''))
            return lines

        def __str__(self):
            """Return single string representation of self."""
            return string.join(self.lines(), '')

    def __init__(self):
        """Initialize self from config file, parsing out interesting content."""
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
        """Return copy of stored lines updated by current metadata."""
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
                    if iface_name in self.ifaces:
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
                        matches = []
                        for iface in tokens[1:]:
                            if iface in self.autoset:
                                matches.append(iface)
                                found_auto.add(iface)
                        if len(matches) > 0:
                            newlines.append('auto %s\n' % \
                                    string.join(matches, ' '))
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

    def add_iface(self, iface, method):
        """Create a new network interface stanza with minimal info."""
        line = "iface %s inet %s\n" % (iface, method)
        stanza = self.InterfaceStanza(line)
        self.ifaces[stanza.iface] = stanza
        return section

    def __str__(self):
        """Return entire config file as string, modified by current metadata."""
        return string.join(self._update_lines(), '')

    def write(self, makeBackup = True):
        """Rewrite the config file, perhaps making a backup of the old one."""
        self.lines = self._update_lines()
        ConfigFileBase.write(self, makeBackup)

if __name__ == '__main__':
    """Test these classes in a limited way."""

    print "==================================================="
    print "Parsing /etc/hostname"
    print "==================================================="
    o = EtcHostname()
    print "* Hostname =", o.hostname
    print "* File contents:\n----------------\n%s" % str(o)

    print "==================================================="
    print "Parsing /etc/resolv.conf"
    print "==================================================="
    o = EtcResolvConf()
    print "* Nameservers =", o.nameservers
    print "* File contents:\n----------------\n%s" % str(o)

    print "==================================================="
    print "Parsing /etc/hosts"
    print "==================================================="
    o = EtcHosts()
    print "* IPs =", o.ips
    print "* File contents:\n----------------\n%s" % str(o)

    print "==================================================="
    print "Parsing /etc/wvdial.conf"
    print "==================================================="
    o = EtcWvdialConf()
    print "* Metadata =", o.metadata
    print "* File contents:\n----------------\n%s" % str(o)

    print "==================================================="
    print "Parsing /etc/ppp/peers/dod"
    print "==================================================="
    o = EtcPppPeersDod()
    print "* Metadata =", o.metadata
    print "* File contents:\n----------------\n%s" % str(o)

    print "==================================================="
    print "Parsing /etc/dhcp3/dhclient.conf"
    print "==================================================="
    o = EtcDhcp3DhclientConf()
    print "* Nameservers =", o.nameservers
    print "* File contents:\n----------------\n%s" % str(o)

    print "==================================================="
    print "Parsing /etc/dhcp3/dhcp.conf"
    print "==================================================="
    o = EtcDhcp3DhcpConf()
    print "* Subnets =", o.subnets
    print "* File contents:\n----------------\n%s" % str(o)

    print "==================================================="
    print "Parsing /etc/network/interfaces"
    print "==================================================="
    o = EtcNetworkInterfaces()
    print "* Auto Start =", o.autoset
    print "* Interfaces =", o.ifaces
    print "* File contents:\n----------------\n%s" % str(o)

