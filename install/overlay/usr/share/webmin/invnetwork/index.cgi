#!/usr/bin/perl

# index.cgi for invnetwork - draw Inveneo Networking Webmin page

# external resources
do '../web-lib.pl';
&init_config();
do '../ui-lib.pl';
use Data::Dumper;
use URI::Escape;

$ERR_PREFIX = 'err_';

# draw the page
&ui_print_header(undef, $module_info{'desc'}, "");     

print "<style type='text/css'>\n";
print "p.good {";
print " border-style: solid; border-width: thin; padding: 0.5em;";
print " color: green}\n";
print "p.bad  {";
print " border-style: solid; border-width: thin; padding: 0.5em;";
print " color: red}\n";
print "</style>\n";

$error_string = &get_cgi;
if ($error_string eq "") {
#    foreach $key (keys %in) {
#        print "'" . $key . "'='" . $in{$key} . "'<br>";
#    }
    if ($in{'good_news'}) {
        print "<p class='good'>" . $in{'good_news'} . "</p><br>";
    }
    if ($in{'bad_news'}) {
        print "<p class='bad'>" . $in{'bad_news'} . "</p><br>";
    }
    &draw_form;
} else {
    print &in_red('Internal Error:') . "<br>";
    print "<pre>" . $error_string . "</pre>";
}

&ui_print_footer("/", $text{'index'});
exit;

sub in_red {
    local ($text) = @_;
    return "<font color='red'>" . $text . "</font>";
}

sub error_text {
    local ($key) = @_;
    if ($in{$ERR_PREFIX . $key}) {
        return "<p class='bad'>" . $in{$ERR_PREFIX . $key} . "</p>";
    }
    return "";
}

# Fill global %in with CGI parameters, else from output of scanConfig.py
# Returns "" on success, else an error string
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
    print &name_stuff;
    print "<br>\n";
    print &wan_stuff;
    print "<br>\n";
    print &lan_stuff;
    print &ui_submit('Apply Changes');
    print &ui_form_end();
}

sub name_stuff {
    local $s = "<h2>Network Names</h2>\n";
    $s .= "<table border>\n";

    $s .= "<tr><td align='right' width='20%'>Hostname: </td>\n";
    $s .= "<td width='20%'>" .
        &ui_textbox('hostname', $in{'hostname'}, 20) . "</td>\n";
    $s .= "<td>" . &error_text('hostname') . "</td></tr>\n";

    $s .= "<tr><td align='right' width='20%'>Primary DNS: </td>\n";
    $s .= "<td width='20%'>" .
        &ui_textbox('dns_0', $in{'dns_0'}, 20) . "</td>\n";
    $s .= "<td>" . &error_text('dns_0') . "</td></tr>\n";

    $s .= "<tr><td align='right' width='20%'>Secondary DNS: </td>\n";
    $s .= "<td width='20%'>" .
        &ui_textbox('dns_1', $in{'dns_1'}, 20) . "</td>\n";
    $s .= "<td>" . &error_text('dns_1') . "</td></tr>\n";

    $s .= "</table>\n";
    return $s;
}

sub wan_stuff {
    local $s = "<h2>WAN</h2>\n";
    $s .= "<table border>\n";

    $s .= "<tr><td>" . &error_text('wan_interface') . "</td></tr>\n";

    $s .= "<tr><td>" . &ui_radio_table('wan_interface', $in{'wan_interface'},
        [ [ 'off',      'Off',      '&nbsp;' ],
          [ 'ethernet', 'Ethernet', &eth0_stuff ],
          [ 'modem',    'Modem',    &modem_stuff ] ]) .
        "</td></tr>\n";

    $s .= "</table>\n";
    return $s;
}

sub eth0_stuff {
    local $s = "<table border>\n";

    $s .= "<tr><td>" . &error_text('wan_method') . "</td></tr>\n";

    $s .= "<tr><td>" . &ui_radio_table('wan_method', $in{'wan_method'},
        [ ['dhcp',   'DHCP Client', '&nbsp'],
          ['static', 'Static', &eth0_static_stuff] ]) .
        "</td></tr>\n";

    $s .= "</table>\n";
    return $s;
}

sub eth0_static_stuff {
    local $s = "<table border>\n";

    $s .= "<tr><td align='right'>IP Address: </td>\n";
    $s .= "<td>". &ui_textbox('wan_address', $in{'wan_address'}, 20). "</td>\n";
    $s .= "<td>" . &error_text('wan_address') . "</td></tr>\n";

    $s .= "<tr><td align='right'>Netmask: </td>\n";
    $s .= "<td>". &ui_textbox('wan_netmask', $in{'wan_netmask'}, 20). "</td>\n";
    $s .= "<td>" . &error_text('wan_netmask') . "</td></tr>\n";

    $s .= "<tr><td align='right'>Gateway: </td>\n";
    $s .= "<td>". &ui_textbox('wan_gateway', $in{'wan_gateway'}, 20). "</td>\n";
    $s .= "<td>" . &error_text('wan_gateway') . "</td></tr>\n";

    $s .= "</table>\n";
    return $s;
}

sub modem_stuff {
    local $s = "<table border>\n";

    $s .= "<tr><td align='right'>Device: </td>\n";
    $s .= "<td>" . &ui_textbox('ppp_modem', $in{'ppp_modem'}, 20) . "</td>\n";
    $s .= "<td>" . &error_text('ppp_modem') . "</td></tr>\n";

    $s .= "<tr><td align='right'>Phone Number: </td>\n";
    $s .= "<td>" . &ui_textbox('ppp_phone', $in{'ppp_phone'}, 20) . "</td>\n";
    $s .= "<td>" . &error_text('ppp_phone') . "</td></tr>\n";

    $s .= "<tr><td align='right'>Username: </td>\n";
    $s .= "<td>" . &ui_textbox('ppp_username', $in{'ppp_username'}, 20) .
        "</td>\n";
    $s .= "<td>" . &error_text('ppp_username') . "</td></tr>\n";

    $s .= "<tr><td align='right'>Password: </td>\n";
    $s .= "<td>" . &ui_password('ppp_password', $in{'ppp_password'}, 20) .
        "</td>\n";
    $s .= "<td>" . &error_text('ppp_password') . "</td></tr>\n";

    $s .= "<tr><td align='right'>Baud Rate: </td>\n";
    $s .= "<td>" . &ui_textbox('ppp_baud', $in{'ppp_baud'}, 20). "</td>\n";
    $s .= "<td>" . &error_text('ppp_baud') . "</td></tr>\n";

    $s .= "<tr><td align='right'>Idle (secs): </td>\n";
    $s .= "<td>" .
        &ui_textbox('ppp_idle_seconds', $in{'ppp_idle_seconds'}, 20) .
        "</td>\n";
    $s .= "<td>" . &error_text('ppp_idle_seconds') . "</td></tr>\n";

    $s .= "<tr><td align='right'>Init String 1: </td>\n";
    $s .= "<td>" . &ui_textbox('ppp_init1', $in{'ppp_init1'}, 20) . "</td>\n";
    $s .= "<td>" . &error_text('ppp_init1') . "</td></tr>\n";

    $s .= "<tr><td align='right'>Init String 2: </td>\n";
    $s .= "<td>" . &ui_textbox('ppp_init2', $in{'ppp_init2'}, 20) . "</td>\n";
    $s .= "<td>" . &error_text('ppp_init2') . "</td></tr>\n";

    $s .= "</table>\n";
    return $s;
}

sub lan_stuff {
    local $s = "<h2>LAN</h2>\n";

    $s .= &ui_hidden('lan_netmask', $in{'lan_netmask'});
    $s .= &ui_hidden('lan_dhcp_was_on', $in{'lan_dhcp_on'});
    $s .= &error_text('lan_netmask');
    $s .= &error_text('lan_network');
    $s .= &error_text('lan_network_range');

    $s .= "<table border>\n";

    $s .= "<tr><td align='right' width='20%'>IP Address: </td>\n";
    $s .= "<td width='20%'>" .
        &ui_textbox('lan_address', $in{'lan_address'}, 20) . "</td>\n";
    $s .= "<td>" . &error_text('lan_address') . "</td></tr>\n";

    $s .= "<tr><td align='right' width='20%'>Gateway: </td>\n";
    $s .= "<td width='20%'>" .
        &ui_textbox('lan_gateway', $in{'lan_gateway'}, 20) . "</td>\n";
    $s .= "<td>" . &error_text('lan_gateway') . "</td></tr>\n";

    $s .= "<tr><td align='right' width='20%'>&nbsp;</td>\n";
    $s .= "<td width='20%'>" .
        &ui_checkbox('lan_dhcp_on', 'on', 'DHCP Server On',
            $in{'lan_dhcp_on'} eq 'on') .
        "</td>\n";
    $s .= "<td>" . &error_text('lan_dhcp_on') . "</td></tr>\n";

    $s .= "<tr><td align='right' width='20%'>DHCP Address Range: </td>\n";
    $s .= "<td width='20%'>" .
        &ui_textbox('lan_dhcp_range_start', $in{'lan_dhcp_range_start'}, 3) .
        " to " .
        &ui_textbox('lan_dhcp_range_end', $in{'lan_dhcp_range_end'}, 3) .
        "</td>\n";
    $s .= "<td>" . &error_text('lan_dhcp_range_start') .
        &error_text('lan_dhcp_range_end') . "</td></tr>\n";

    $s .= "</table>\n";
    return $s;
}
