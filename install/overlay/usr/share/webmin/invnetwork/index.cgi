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

sub trim {
    local($str) = @_;
    $str =~ s/^\s+//;
    $str =~ s/\s+$//;
    return $str;
}

sub print_value_attr {
    local($value) = @_;
    print " value='" . $value . "'";
}

sub print_wan_static_stuff {
    print <<EOF;
        <table border='1'>
        <tr>
            <td align='right'>IP Address:</td>
            <td><input type='text' name='wan_address'
EOF
    &print_value_attr($assoc{"wan_address"});
    print <<EOF;
            ></td>
        </tr>
        <tr>
            <td align='right'>Netmask:</td>
            <td><input type='text' name='wan_netmask'
EOF
    &print_value_attr($assoc{"wan_netmask"});
    print <<EOF;
            ></td>
        </tr>
        <tr>
            <td align='right'>Gateway:</td>
            <td><input type='text' name='wan_gateway'
EOF
    &print_value_attr($assoc{"wan_gateway"});
    print <<EOF;
            ></td>
        </tr>
        </table>
EOF
}

sub print_wan_stuff {
    print <<EOF;
    <table border='1'>
    <tr><th>Type</th><th>&nbsp;</th></tr>
    <tr>
        <td><input type='radio' name='wan_type' value='dhcp'
EOF
    if ($assoc{'wan_type'} eq 'dhcp') {
        print ' checked';
    }
    print <<EOF;
            >DHCP Client</td>
        <td>&nbsp;</td>
    </tr>
    <tr>
        <td><input type='radio' name='wan_type' value='static'
EOF
    if ($assoc{'wan_type'} eq 'static') {
        print ' checked';
    }
    print <<EOF;
            >Static</td>
        <td>
EOF
    &print_wan_static_stuff;
    print <<EOF;
        </td>
    </tr>
    <tr>
        <td><input type='radio' name='wan_type' value='dialup'
EOF
    if ($assoc{'wan_type'} eq 'dialup') {
        print ' checked';
    }
    print <<EOF;
            >Dialup</td>
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
        <td><input type='text' name='lan_address'
EOF
    &print_value_attr($assoc{"lan_address"});
    print <<EOF;
            ></td>
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

$config_string = `./scanconfig.cgi`;
%assoc = ();
for $pair (split /&/, $config_string) {
    ($key, $value) = split /=/, $pair;
    $assoc{&trim($key)} = &trim($value);
}

#foreach $key (keys %assoc) {
#    print "'" . $key . "'='" . $assoc{$key} . "'<br>";
#}

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

&ui_print_footer("/", $text{'index'});

