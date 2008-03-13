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

$error_string = &get_cgi;
if ($error_string eq "") {
#    foreach $key (keys %in) {
#        print "'" . $key . "'='" . $in{$key} . "'<br>";
#    }
    print "<font color='orange'>" . $in{'message'} . "</font>";
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
    return &in_red($in{$ERR_PREFIX . $key});
}

sub in_a_box {
    local ($html) = @_;
    return '<div style="border: double;">' . $html . '</div>';
}

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
    print &ui_columns_start(['Network', 'Settings']);
    print &ui_columns_row(['WAN', &wan_stuff], ['align="center"', '']);
    print &ui_columns_row(['LAN', &in_a_box(&lan_stuff)],
        ['align="center"', '']);
    print &ui_columns_end();
    print &ui_submit('Submit');
    print &ui_form_end();
    print "<b>Further Operations:</b><br><br>";
    print &ui_form_start('dhcpd-stop.cgi');
    print &ui_submit('Stop DHCP server');
    print &ui_form_end();
    print &ui_form_start('dhcpd-restart.cgi');
    print &ui_submit('Restart DHCP server');
    print &ui_form_end();
}

sub wan_stuff {
    return &ui_radio_table('wan_interface', $in{'wan_interface'},
    [ [ 'off',      'Off',      '&nbsp;' ],
      [ 'ethernet', 'Ethernet', &in_a_box(&eth0_stuff) ],
      [ 'modem',    'Modem',    &in_a_box(&modem_stuff) ]
      ]);
}

sub eth0_stuff {
    return &ui_radio_table('wan_method', $in{'wan_method'},
    [ ['dhcp',   'DHCP Client', '&nbsp'],
      ['static', 'Static', &in_a_box(&eth0_static_stuff)]
      ]);
}

sub eth0_static_stuff {
    return &ui_columns_start() .
    &ui_columns_row(
        ['IP Address:',
        &ui_textbox('wan_address', $in{'wan_address'}, 20),
        &error_text('wan_address')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Netmask:',
        &ui_textbox('wan_netmask', $in{'wan_netmask'}, 20),
        &error_text('wan_netmask')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Gateway:',
        &ui_textbox('wan_gateway', $in{'wan_gateway'}, 20),
        &error_text('wan_gateway')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Primary DNS:',
        &ui_textbox('dns_0', $in{'dns_0'}, 20),
        &error_text('dns_0')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Secondary DNS:',
        &ui_textbox('dns_1', $in{'dns_1'}, 20),
        &error_text('dns_1')],
        ['align="right"', '', '']) .
    &ui_columns_end();
}

sub modem_stuff {
    return &ui_columns_start() .
    &ui_columns_row(
        ['Device:',
        &ui_textbox('ppp_modem', $in{'ppp_modem'}, 20),
        &error_text('ppp_modem')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Phone Number:',
        &ui_textbox('ppp_phone', $in{'ppp_phone'}, 20),
        &error_text('ppp_phone')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Username:',
        &ui_textbox('ppp_username', $in{'ppp_username'}, 20),
        &error_text('ppp_username')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Password:',
        &ui_password('ppp_password', $in{'ppp_password'}, 20),
        &error_text('ppp_password')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Baud:',
        &ui_textbox('ppp_baud', $in{'ppp_baud'}, 20),
        &error_text('ppp_baud')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Idle (secs):',
        &ui_textbox('ppp_idle_seconds', $in{'ppp_idle_seconds'}, 20),
        &error_text('ppp_idle_seconds')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Init1:',
        &ui_textbox('ppp_init1', $in{'ppp_init1'}, 20),
        &error_text('ppp_init1')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Init2:',
        &ui_textbox('ppp_init2', $in{'ppp_init2'}, 20),
        &error_text('ppp_init2')],
        ['align="right"', '', '']) .
    &ui_columns_end();
}

sub lan_stuff {
    return &ui_columns_start() .
    &ui_columns_row(
        ['IP Address:',
        &ui_textbox('lan_address', $in{'lan_address'}, 20),
        &error_text('lan_address')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['Gateway:',
        &ui_textbox('lan_gateway', $in{'lan_gateway'}, 20),
        &error_text('lan_gateway')],
        ['align="right"', '', '']) .
    &ui_columns_row([
        "&nbsp;",
        &ui_checkbox('lan_dhcp_on', 'on', 'DHCP Server On', $in{'lan_dhcp_on'}),
        &error_text('lan_dhcp_on')]) .
    &ui_columns_row(
        ['DHCP Address Range Start:',
        &ui_textbox('lan_dhcp_range_start', $in{'lan_dhcp_range_start'}, 3),
        &error_text('lan_dhcp_range_start')],
        ['align="right"', '', '']) .
    &ui_columns_row(
        ['DHCP Address Range End:',
        &ui_textbox('lan_dhcp_range_end', $in{'lan_dhcp_range_end'}, 3),
        &error_text('lan_dhcp_range_end')],
        ['align="right"', '', '']) .
    &ui_columns_end() .
    &ui_hidden('lan_netmask', '255.255.255.0');
}
