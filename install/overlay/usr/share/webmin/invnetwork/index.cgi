#!/usr/bin/perl

# index.cgi for invnetwork - draw Inveneo Networking Webmin page

# external resources
do '../web-lib.pl';
&init_config();
do '../ui-lib.pl';
use Data::Dumper;
use URI::Escape;

# draw the page
&ui_print_header(undef, $module_info{'desc'}, "", undef, 1, 1);     
$error_string = &get_cgi;
if ($error_string eq "") {
#    foreach $key (keys %in) {
#        print "'" . $key . "'='" . $in{$key} . "'<br>";
#    }
    &draw_form;
} else {
    print "<font color='red'>Internal Error:</font><br>";
    print "<pre>" . $error_string . "</pre>";
}
&ui_print_footer("/", $text{'index'});
exit;

# fill global %in with CGI parameters, else from output of scanConfig.py
# returns "" on success, else an error string
sub get_cgi {

    &ReadParse(); # by default, reads QueryString into global %in
    if (not %in) {
        local $a = \%in;
        %$a = ( );
        $scanconfig = `./scanConfig.py 2>&1`;
        if ($?) {
            return $scanconfig;
        } else {
            @terms = split(/\&/, $scanconfig);
            foreach $term (@terms) {
                local ($k, $v) = split(/=/, $term, 2);
                if (!$_[2]) {
                    $k =~ tr/\+/ /;
                    $v =~ tr/\+/ /;
                }
                $k =~ s/%(..)/pack("c",hex($1))/ge;
                $v =~ s/%(..)/pack("c",hex($1))/ge;
                $a->{$k} = defined($a->{$k}) ? $a->{$k}."\0".$v : $v;
            }
        }
    }
    return "";
}

sub draw_form {
    print &ui_form_start('processForm.cgi', 'post');
    print &ui_table_start();
    print "form here";
    print &ui_table_end();
    print &ui_submit('Submit');
    print &ui_form_end();
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

sub print_wan_ethernet_stuff {
    print <<EOF;
        <table border='1'>
        <tr>
            <td><input type='radio' name='wan_method' value='dhcp'
EOF
    if ($assoc{'wan_method'} eq 'dhcp') { print ' checked'; }
    print <<EOF;
            >DHCP Client</td>
            <td>&nbsp;</td>
        </tr>
        <tr>
            <td><input type='radio' name='wan_method' value='static'
EOF
    if ($assoc{'wan_method'} eq 'static') { print ' checked'; }
    print <<EOF;
            >Static</td>
            <td>
EOF
    &print_wan_static_stuff;
    print <<EOF;
            </td>
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
    <tr><th>Interface</th><th>&nbsp;</th></tr>
    <tr>
        <td><input type='radio' name='wan_interface' value='off'
EOF
    if ($assoc{'wan_interface'} eq 'off') { print ' checked'; }
    print <<EOF;
            >Off</td>
        <td>&nbsp;</td>
    </tr>
    <tr>
        <td><input type='radio' name='wan_interface' value=$WAN_INTERFACE
EOF
    if ($assoc{'wan_interface'} eq $WAN_INTERFACE) { print ' checked'; }
    print <<EOF;
            >Ethernet</td>
        <td>
EOF
    &print_wan_ethernet_stuff;
    print <<EOF;
        </td>
    </tr>
    <tr>
        <td><input type='radio' name='wan_interface' value='modem'
EOF
    if ($assoc{'wan_interface'} eq 'modem') { print ' checked'; }
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
            ><input type='hidden' name='lan_netmask_orig'
EOF
    &print_value_attr($assoc{'lan_netmask'});
    print <<EOF;
            ></td>
    </tr>
    <tr>
        <td align='right'>Gateway:</td>
        <td><input type='text' name='lan_gateway'
EOF
    &print_value_attr($assoc{'lan_gateway'});
    print <<EOF;
            ><input type='hidden' name='lan_gateway_orig'
EOF
    &print_value_attr($assoc{'lan_gateway'});
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
