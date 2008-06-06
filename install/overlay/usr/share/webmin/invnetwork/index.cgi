#!/usr/bin/perl

# index.cgi for invnetwork - draw Inveneo Networking Webmin page

# external resources
do '../web-lib.pl';
&init_config();
do '../ui-lib.pl';
use Data::Dumper;
use URI::Escape;

$ERR_PREFIX = 'err_';

$head_stuff = '
<script type="text/javascript">

function disable_div(the_div, value) {
    var arr = the_div.getElementsByTagName("input");
    for (var i = 0; i < arr.length; i++) {
        arr[i].disabled = value;
    }
}

function wan_interface_eth0() {
    disable_div(document.getElementById("eth0_stuff"), false);
    disable_div(document.getElementById("modem_stuff"), true);
    disable_div(document.getElementById("eth1_stuff"), true);
}

function wan_interface_modem() {
    disable_div(document.getElementById("eth0_stuff"), true);
    disable_div(document.getElementById("modem_stuff"), false);
    disable_div(document.getElementById("eth1_stuff"), true);
}

function wan_interface_eth1() {
    disable_div(document.getElementById("eth0_stuff"), true);
    disable_div(document.getElementById("modem_stuff"), true);
    disable_div(document.getElementById("eth1_stuff"), false);
}

function wan_method_dhcp() {
    disable_div(document.getElementById("eth0_static_stuff"), true);
}

function wan_method_static() {
    disable_div(document.getElementById("eth0_static_stuff"), false);
}

function lan_dhcp_on_on() {
    disable_div(document.getElementById("eth1_dhcp_range_stuff"), false);
}

function lan_dhcp_on_off() {
    disable_div(document.getElementById("eth1_dhcp_range_stuff"), true);
}
</script>

<style type="text/css">
p.good {
    border-style: solid;
    border-width: thin;
    padding: 0.5em;
    color: green;
}
p.bad  {
    border-style: solid;
    border-width: thin;
    padding: 0.5em;
    color: red;
}
table.wide {
    border-width: 1px;
    border-style: solid;
    width: 100%;
}

td.label {
    text-align: right;
    width: 20%;
}
td.entry {
    width: 20%;
    background-color: #FFFFEE;
    text-align: left;
}
td.error {
    text-align: left;
}

td.indent {
    width: 10%;
}
</style>';

# draw the page... this comment from web-lib-funcs.pl may be helpful:
# header(title, image, [help], [config], [nomodule], [nowebmin], [rightside],
# #        [head-stuff], [body-stuff], [below])
# # Output a page header with some title and image. The header may also
# # include a link to help, and a link to the config page.
# # The header will also have a link to to webmin index, and a link to the
# # module menu if there is no config link
#
&ui_print_header(undef, $module_info{'desc'}, undef, undef, undef, undef,
    undef, undef, $head_stuff, undef, undef); 

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

sub my_radio {
    local ($ctl, $val) = @_;
    $checked = ($in{$ctl} eq $val) ? ' checked ' : ' ';
    return '<input type="radio" name="' . $ctl . '" value="' . $val . '"' .
        $checked . 'onClick="' . $ctl.'_'.$val . '();">';
}

sub my_textbox {
    local ($name) = @_;
    return '<input name="' . $name . '" value="' . $in{$name} . '" size="20">';
}

sub my_textbox3 {
    local ($name) = @_;
    return '<input name="' . $name . '" value="' . $in{$name} . '" size="3">';
}

sub my_password {
    local ($name) = @_;
    return '<input type="password" name="' . $name . '" value="' .
        $in{$name} . '" size="20">';
}

sub draw_form {
    print &ui_form_start('processForm.cgi', 'post');
    print &host_stuff;
    print "<br>\n";
    print &wan_stuff;
    print "<br>\n";
    print &dns_stuff;
    print "<br>\n";
    print &lan_stuff;
    print &hidden_values;
    print "<br>\n";
    print "<input type='submit' value='Apply Changes'>\n";
    print &ui_form_end();
}

sub host_stuff {
    return '
<div id="host_stuff">
<table class="wide">
<tr>
  <td class="label">Hub Hostname:</td>
  <td class="entry">' . &my_textbox('hostname') . '</td>
  <td class="error">' . &error_text('hostname') . '</td>
</tr>
</table>
</div>
';
}

sub wan_stuff {
    return '
<div id="wan_stuff">
<h2>Connection to the Internet</h2>
<table class="wide">
<tr>
  <td colspan="2">' . &error_text('wan_interface') . '</td>
</tr>
<tr>
  <td colspan="2">' . &my_radio('wan_interface', 'eth0') .
    'WAN Port connection to Internet</td>
</tr>
<tr>
  <td class="indent"></td>
  <td>' . &eth0_stuff . '</td>
</tr>
<tr>
  <td colspan="2">' . &my_radio('wan_interface', 'modem') .
    'Modem connection to Internet</td>
</tr>
<tr>
  <td class="indent"></td>
  <td>' . &modem_stuff . '</td>
</tr>
<tr>
  <td colspan="2">' . &my_radio('wan_interface', 'eth1') .
    'LAN Port connection to Internet</td>
</tr>
<tr>
  <td class="indent"></td>
  <td>' . &eth1_stuff . '</td>
</tr>
</table>
</div>
';
}

sub eth0_stuff {
    return '
<div id="eth0_stuff">
<table class="wide">
<tr>
  <td colspan="2">' . &error_text('wan_method') . '</td>
</tr>
<tr>
  <td colspan="2">' . &my_radio('wan_method', 'dhcp') .
    'DHCP provides setup</td>
</tr>
<tr>
  <td colspan="2">' . &my_radio('wan_method', 'static') .
    'Static setup</td>
</tr>
<tr>
  <td class="indent"></td>
  <td>' . &eth0_static_stuff . '</td>
</tr>
</table>
</div>
';
}

sub eth0_static_stuff {
    return '
<div id="eth0_static_stuff">
<table class="wide">
<tr>
  <td class="label">IP Address:</td>
  <td class="entry">' . &my_textbox('wan_address') . '</td>
  <td class="error">' . &error_text('wan_address') . '</td>
</tr>
<tr>
  <td class="label">Netmask:</td>
  <td class="entry">' . &my_textbox('wan_netmask') . '</td>
  <td class="error">' . &error_text('wan_netmask') . '</td>
</tr>
<tr>
  <td class="label">Gateway:</td>
  <td class="entry">' . &my_textbox('wan_gateway') . '</td>
  <td class="error">' . &error_text('wan_gateway') . '</td>
</tr>
</table>
</div>
';
}

sub modem_stuff {
    return '
<div id="modem_stuff">
<table class="wide">
<tr>
  <td class="label">Modem Device:</td>
  <td class="entry">' . &my_textbox('ppp_modem') . '</td>
  <td class="error">' . &error_text('ppp_modem') . '</td>
</tr>
<tr>
  <td class="label">Phone Number:</td>
  <td class="entry">' . &my_textbox('ppp_phone') . '</td>
  <td class="error">' . &error_text('ppp_phone') . '</td>
</tr>
<tr>
  <td class="label">Username:</td>
  <td class="entry">' . &my_textbox('ppp_username') . '</td>
  <td class="error">' . &error_text('ppp_username') . '</td>
</tr>
<tr>
  <td class="label">Password:</td>
  <td class="entry">' . &my_password('ppp_password') . '</td>
  <td class="error">' . &error_text('ppp_password') . '</td>
</tr>
<tr>
  <td class="label">Baud Rate:</td>
  <td class="entry">' . &my_textbox('ppp_baud'). '</td>
  <td class="error">' . &error_text('ppp_baud') . '</td>
</tr>
<tr>
  <td class="label">Idle (secs):</td>
  <td class="entry">' . &my_textbox('ppp_idle_seconds') . '</td>
  <td class="error">' . &error_text('ppp_idle_seconds') . '</td>
</tr>
<tr>
  <td class="label">Init String 1:</td>
  <td class="entry">' . &my_textbox('ppp_init1') . '</td>
  <td class="error">' . &error_text('ppp_init1') . '</td>
</tr>
<tr>
  <td class="label">Init String 2:</td>
  <td class="entry">' . &my_textbox('ppp_init2') . '</td>
  <td class="error">' . &error_text('ppp_init2') . '</td>
</tr>
</table>
</div>
';
}

sub eth1_stuff {
    return '
<div id="eth1_stuff">
<table class="wide">
  <tr>
    <td class="label">Gateway:</td>
    <td class="entry">' . &my_textbox('lan_gateway') . '</td>
    <td class="error">' . &error_text('lan_gateway') . '</td>
  </tr>
</table>
</div>
';
}

sub dns_stuff {
    return '
<div id="dns_stuff">
<table class="wide">
<tr>
  <td class="label">External DNS Server(s):</td>
  <td class="entry">' . &my_textbox('dns_0') . '<br/>' .
    &my_textbox('dns_1') . '</td>
  <td class="error">' .
    &error_text('dns_0') . '<br/>' .
    &error_text('dns_1') . '</td>
  </td>
</tr>
</table>
</div>
';
}

sub lan_stuff {
    return '
<div id="lan_stuff">
<h2>Connection to Local Area Network</h2>' .
&eth1_static_stuff .
&eth1_dhcp_stuff . '
</div>
';
}

sub eth1_static_stuff {
    return '
<div id="eth1_static_stuff">
<table class="wide">
<tr>
  <td colspan="3">' .
    &error_text('lan_network') . '<br/>' .
    &error_text('lan_network_range') . '</td>
</tr>
<tr>
  <td class="label">Hub&apos;s address on LAN:</td>
  <td class="entry">' . &my_textbox('lan_address') . '</td>
  <td class="error">' . &error_text('lan_address') . '</td>
</tr>
</table>
</div>
';
}

sub eth1_dhcp_stuff {
    return '
<div id="eth1_dhcp_stuff">
<table class="wide">
<tr>
  <td colspan="2">' . &my_radio('lan_dhcp_on', 'on') .
    'Hub is a DHCP server</td>
</tr>
<tr>
  <td class="indent"></td>
  <td>' . &eth1_dhcp_range_stuff . '</td>
</tr>
<tr>
  <td colspan="2">' . &my_radio('lan_dhcp_on', 'off') .
    'Hub is not serving DHCP</td>
</tr>
</table>
</div>
';
}

sub eth1_dhcp_range_stuff {
    return '
<div id="eth1_dhcp_range_stuff">
<table class="wide">
<tr>
  <td>Address range:' .
    &my_textbox3('lan_dhcp_range_start') . ' to ' .
    &my_textbox3('lan_dhcp_range_end') . '</td>
  <td class="error">' .
    &error_text('lan_dhcp_range_start') . '<br/>' .
    &error_text('lan_dhcp_range_end') . '</td>
</tr>
</table>
</div>
';
}

sub hidden_values {
    return '
<input type="hidden" name="lan_netmask" value="255.255.255.0">
<input type="hidden" name="lan_dhcp_was_on" value="' . $in{'lan_dhcp_on'} . '">
';
}
