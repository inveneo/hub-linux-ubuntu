#!/usr/bin/perl

# Either redirects to link.cgi, if a URL has been set, or asks for a URL
require './invnetwork-lib.pl';
require '../invlib/form.pm';
require '../dhcpd/dhcpd-lib.pl';
use Data::Dumper;
use dhcp;

&ReadParse();

use constant WAN_INTERFACE => "eth0";
use constant LAN_INTERFACE => "eth1";

$msg = $in{'msg'};

&ui_print_header(undef, $module_info{'desc'}, "", undef, 1, 1);     
if ( $msg ) {
    print "<h4>" . un_urlize($msg) . "</h4><br>";
}

sub print_wan_static_stuff {
    print <<EOF;
        <table border='1'>
        <tr>
            <td align='right'>IP Address:</td>
            <td><input type='text' name='wan_address'></td>
        </tr>
        <tr>
            <td align='right'>Netmask:</td>
            <td><input type='text' name='wan_netmask'></td>
        </tr>
        <tr>
            <td align='right'>Gateway:</td>
            <td><input type='text' name='wan_gateway'></td>
        </tr>
        </table>
EOF
}

sub print_wan_stuff {
    print <<EOF;
    <table border='1'>
    <tr><th>Type</th><th>&nbsp;</th></tr>
    <tr>
        <td><input type='radio' name='wan_type' value='dhcp'>DHCP Client</td>
        <td>&nbsp;</td>
    </tr>
    <tr>
        <td><input type='radio' name='wan_type' value='static'>Static</td>
        <td>
EOF
    &print_wan_static_stuff;
    print <<EOF;
        </td>
    </tr>
    <tr>
        <td><input type='radio' name='wan_type' value='dialup'>Dialup</td>
        <td>&nbsp;</td>
    </tr>
    </table>
EOF
}

sub print_lan_stuff {
    print <<EOF;
    <table border='1'>
    <tr>
        <td align='right'>IP Address:</td>
        <td><input type='text' name='lan_address'></td>
    </tr>
    <tr>
        <td align='right'>DHCP On:</td>
        <td><input type='checkbox' name='lan_dhcp_on'></td>
    </tr>
    <tr>
        <td align='right'>DHCP Address Range:</td>
        <td><input type='text' name='lan_dhcp_range'></td>
    </tr>
    </table>
EOF
}

print <<EOF;
<form action='process.cgi' method='post'>
<table border='1'>
<tr><th>Interface</th><th>&nbsp;</th></tr>
<tr><td>WAN</td><td>
EOF

&print_wan_stuff;

print <<EOF;
</td></tr>
<tr><td>LAN</td><td>
EOF

&print_lan_stuff;

print <<EOF;
</td></tr>
</table>
<input type='submit' value='Submit'>
</form>
EOF

print `scanconfig.cgi`;

&ui_print_footer("/", $text{'index'});

