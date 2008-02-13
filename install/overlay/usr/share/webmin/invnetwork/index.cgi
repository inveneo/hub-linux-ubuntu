#!/usr/bin/perl

# Either redirects to link.cgi, if a URL has been set, or asks for a URL
require './invnetwork-lib.pl';
require '../invlib/form.pm';
require '../dhcpd/dhcpd-lib.pl';
use Data::Dumper;
use dhcp;
use URI::Escape;

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
    &print_value_attr($assoc{'wan_address'});
    print <<EOF;
            ></td>
        </tr>
        <tr>
            <td align='right'>Netmask:</td>
            <td><input type='text' name='wan_netmask'
EOF
    &print_value_attr($assoc{'wan_netmask'});
    print <<EOF;
            ></td>
        </tr>
        <tr>
            <td align='right'>Gateway:</td>
            <td><input type='text' name='wan_gateway'
EOF
    &print_value_attr($assoc{'wan_gateway'});
    print <<EOF;
            ></td>
        </tr>
        </table>
EOF
}

sub print_ppp_stuff {
    print <<EOF;
        <table border='1'>
        <tr>
            <td align='right'>Device:</td>
            <td><input type='text' name='ppp_modem'
EOF
    &print_value_attr($assoc{'ppp_modem'});
    print <<EOF;
            ></td>
        </tr>
        <tr>
            <td align='right'>Phone Number:</td>
            <td><input type='text' name='ppp_phone'
EOF
    &print_value_attr($assoc{'ppp_phone'});
    print <<EOF;
            ></td>
        </tr>
        <tr>
            <td align='right'>Username:</td>
            <td><input type='text' name='ppp_username'
EOF
    &print_value_attr($assoc{'ppp_username'});
    print <<EOF;
            ></td>
        </tr>
        <tr>
            <td align='right'>Password:</td>
            <td><input type='password' name='ppp_password'
EOF
    &print_value_attr($assoc{'ppp_password'});
    print <<EOF;
            ></td>
        </tr>
        <tr>
            <td align='right'>Baud:</td>
            <td><input type='text' name='ppp_baud'
EOF
    &print_value_attr($assoc{'ppp_baud'});
    print <<EOF;
            ></td>
        </tr>
        <tr>
            <td align='right'>Idle (secs):</td>
            <td><input type='text' name='ppp_idle_seconds'
EOF
    &print_value_attr($assoc{'ppp_idle_seconds'});
    print <<EOF;
            ></td>
        </tr>
        <tr>
            <td align='right'>Init1:</td>
            <td><input type='text' name='ppp_init1'
EOF
    &print_value_attr($assoc{'ppp_init1'});
    print <<EOF;
            ></td>
        </tr>
        <tr>
            <td align='right'>Init2:</td>
            <td><input type='text' name='ppp_init2'
EOF
    &print_value_attr($assoc{'ppp_init2'});
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
    if ($assoc{'wan_type'} eq 'dhcp') { print ' checked'; }
    print <<EOF;
            >DHCP Client</td>
        <td>&nbsp;</td>
    </tr>
    <tr>
        <td><input type='radio' name='wan_type' value='static'
EOF
    if ($assoc{'wan_type'} eq 'static') { print ' checked'; }
    print <<EOF;
            >Static</td>
        <td>
EOF
    &print_wan_static_stuff;
    print <<EOF;
        </td>
    </tr>
    <tr>
        <td><input type='radio' name='wan_type' value='modem'
EOF
    if ($assoc{'wan_type'} eq 'modem') { print ' checked'; }
    print <<EOF;
            >Modem</td>
        <td>
EOF
    &print_ppp_stuff;
    print <<EOF;
        </td>
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
    &print_value_attr($assoc{'lan_address'});
    print <<EOF;
            ><input type='hidden' name='lan_address_orig'
EOF
    &print_value_attr($assoc{'lan_address'});
    print <<EOF;
            ></td>
    </tr>
    <tr>
        <td align='right'>Netmask:</td>
        <td><input type='text' name='lan_netmask'
EOF
    &print_value_attr($assoc{'lan_netmask'});
    print <<EOF;
            ><input type='text' name='lan_netmask_orig'
EOF
    &print_value_attr($assoc{'lan_netmask'});
    print <<EOF;
            ></td>
    </tr>
    <tr>
        <td align='right'>DHCP Server On:</td>
        <td><input type='checkbox' name='lan_dhcp_on'
EOF
    print $assoc{'lan_dhcp_on'} ? " checked" : "";
    print <<EOF;
            ></td>
    </tr>
    <tr>
        <td align='right'>DHCP Address Range:</td>
        <td><input type='text' name='lan_dhcp_range_start' size='3'
EOF
    &print_value_attr($assoc{'lan_dhcp_range_start'});
    print "> to <input type='text' name='lan_dhcp_range_end' size='3'";
    &print_value_attr($assoc{'lan_dhcp_range_end'});
    print <<EOF;
            ></td>
    </tr>
    </table>
EOF
}

sub print_page {
    local($config_string) = @_;

    %assoc = ();
    for $pair (split /&/, $config_string) {
        ($key, $value) = split /=/, $pair;
        $assoc{$key} = uri_unescape($value);
    }

#    foreach $key (keys %assoc) {
#        print "'" . $key . "'='" . $assoc{$key} . "'<br>";
#    }

    print <<EOF;
    <form action='processForm.cgi' method='post'>
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
}

# call Python script to glean config values from several files
$config_string = `./scanConfig.cgi 2>&1`;
if ($?) {
    print "<font color='red'>Internal Error</font><br>";
    print "<pre>" . $config_string . "</pre>";
} else {
    &print_page($config_string);
}
&ui_print_footer("/", $text{'index'});
