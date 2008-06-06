#!/usr/bin/perl

# index.cgi for invnetwork - draw Inveneo Networking Webmin page

# external resources
do '../web-lib.pl';
&init_config();
do '../ui-lib.pl';
use Data::Dumper;
use URI::Escape;

$ERR_PREFIX = 'err_';

$head_stuff = '<script type="text/javascript">
function getStyleObject(objectId) {
    if (document.getElementById && document.getElementById(objectId)) {
        return document.getElementById(objectId).style;
    } else if (document.all && document.all(objectId)) {
        return document.all(objectId).style;
    }
    return false;
}

function wan_interface_eth0(setting) {
    var arr = document.getElementsByClassName("wan_interface_eth0");
    for (i = 0; i < arr.length; i++) {
        arr[i].disabled = setting;
    }
    wan_interface_modem(false);
    wan_interface_eth1(false);
}

function wan_interface_modem(setting) {
    var arr = document.getElementsByClassName("wan_interface_modem");
    for (i = 0; i < arr.length; i++) {
        arr[i].disabled = setting;
    }
    wan_interface_eth0(false);
    wan_interface_eth1(false);
}

function wan_interface_eth1(setting) {
    var arr = document.getElementsByClassName("wan_interface_eth1");
    for (i = 0; i < arr.length; i++) {
        arr[i].disabled = setting;
    }
    wan_interface_eth0(false);
    wan_interface_modem(false);
}

function wan_method_dhcp(setting) {
    var arr = document.getElementsByClassName("wan_method_dhcp");
    for (i = 0; i < arr.length; i++) {
        arr[i].disabled = setting;
    }
    wan_method_static(false);
}

function wan_method_static(setting) {
    var arr = document.getElementsByClassName("wan_method_static");
    for (i = 0; i < arr.length; i++) {
        arr[i].disabled = setting;
    }
    wan_method_dhcp(false);
}

function lan_dhcp_on_on(setting) {
}

function lan_dhcp_on_off(setting) {
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

sub draw_form {
    print &ui_form_start('processForm.cgi', 'post');
    print &host_stuff;
    print "<br>\n";
    print &wan_stuff;
    print "<br>\n";
    print &lan_stuff;
    print "<br>\n";
    print &ui_submit('Apply Changes');
    print &hidden_values;
    print &ui_form_end();
}

sub host_stuff {
    return '
<table class="wide">
<tr>
  <td class="label">Hub Hostname:</td>
  <td class="entry">
    <input name="hostname" value="' . $in{'hostname'} . '" size="20">
  </td>
  <td class="error">' . &error_text('hostname') . '</td>
</tr>
</table>
';
}

sub my_radio {
    local ($ctl, $val) = @_;
    $checked = ($in{$ctl} eq $val) ? ' checked ' : ' ';
    return '<input type="radio" name="' . $ctl . '" value="' . $val . '"' .
        $checked . 'onClick="' . $ctl.'_'.$val . '(true)">';
}

sub wan_stuff {
    return '
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
  <td>' . &eth0_stuff . '
  </td>
</tr>
<tr>
  <td colspan="2">' . &my_radio('wan_interface', 'modem') .
    'Modem connection to Internet</td>
</tr>
<tr>
  <td class="indent"></td>
  <td>' . &modem_stuff . '
  </td>
</tr>
<tr>
  <td colspan="2">' . &my_radio('wan_interface', 'eth1') .
    'LAN Port connection to Internet</td>
</tr>
<tr>
  <td class="indent"></td>
  <td>' . &eth1_stuff . '
  </td>
</tr>
</table>

<table class="wide">
<tr>
  <td class="label">External DNS Server(s):<br/></td>
  <td class="entry">
    <input name="dns_0" value="' . $in{'dns_0'} . '" size="20"><br/>
    <input name="dns_1" value="' . $in{'dns_1'} . '" size="20">
  </td>
  <td align="left">' . &error_text('dns_0') . '<br/>' .
    &error_text('dns_1') . '</td>
  </td>
</tr>
</table>
';
}

sub eth0_stuff {
    return '
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
  <td>' . &eth0_static_stuff . '
  </td>
</tr>
</table>
';
}

sub eth0_static_stuff {
    return '
<table class="wide">
<tr>
  <td class="label">IP Address:</td>
  <td>' . &ui_textbox('wan_address', $in{'wan_address'}, 20) . '</td>
  <td>' . &error_text('wan_address') . '</td>
</tr>
<tr>
  <td class="label">Netmask:</td>
  <td>' . &ui_textbox('wan_netmask', $in{'wan_netmask'}, 20) . '</td>
  <td>' . &error_text('wan_netmask') . '</td>
</tr>
<tr>
  <td class="label">Gateway:</td>
  <td>' . &ui_textbox('wan_gateway', $in{'wan_gateway'}, 20). '</td>
  <td>' . &error_text('wan_gateway') . '</td>
</tr>
</table>
';
}

sub modem_stuff {
    return '
<table class="wide">
<tr>
  <td class="label">Modem Device:</td>
  <td>' . &ui_textbox('ppp_modem', $in{'ppp_modem'}, 20) . '</td>
  <td>' . &error_text('ppp_modem') . '</td>
</tr>
<tr>
  <td class="label">Phone Number:</td>
  <td>' . &ui_textbox('ppp_phone', $in{'ppp_phone'}, 20) . '</td>
  <td>' . &error_text('ppp_phone') . '</td>
</tr>
<tr>
  <td class="label">Username:</td>
  <td>' . &ui_textbox('ppp_username', $in{'ppp_username'}, 20) . '</td>
  <td>' . &error_text('ppp_username') . '</td>
</tr>
<tr>
  <td class="label">Password:</td>
  <td>' . &ui_password('ppp_password', $in{'ppp_password'}, 20) . '</td>
  <td>' . &error_text('ppp_password') . '</td>
</tr>
<tr>
  <td class="label">Baud Rate:</td>
  <td>' . &ui_textbox('ppp_baud', $in{'ppp_baud'}, 20). '</td>
  <td>' . &error_text('ppp_baud') . '</td>
</tr>
<tr>
  <td class="label">Idle (secs):</td>
  <td>' . &ui_textbox('ppp_idle_seconds', $in{'ppp_idle_seconds'}, 20) . '</td>
  <td>' . &error_text('ppp_idle_seconds') . '</td>
</tr>
<tr>
  <td class="label">Init String 1:</td>
  <td>' . &ui_textbox('ppp_init1', $in{'ppp_init1'}, 20) . '</td>
  <td>' . &error_text('ppp_init1') . '</td>
</tr>
<tr>
  <td class="label">Init String 2:</td>
  <td>' . &ui_textbox('ppp_init2', $in{'ppp_init2'}, 20) . '</td>
  <td>' . &error_text('ppp_init2') . '</td>
</tr>
</table>
';
}

sub eth1_stuff {
    return '
<table class="wide">
  <tr>
    <td class="label">Gateway:</td>
    <td class="entry">
      <input name="lan_gateway" size="20" class="wan_interface_eth1"
                value="' . $in{'lan_gateway'} . '">
    </td>
    <td align="left">' . &error_text('hostname') . '</td>
  </tr>
</table>
';
}

sub lan_stuff {
    return '
<h2>Connection to Local Area Network</h2>

<table class="wide">
<tr>
  <td class="label">Hub&apos;s address on LAN:</td>
  <td>' . &ui_textbox('lan_address', $in{'lan_address'}, 20) . '</td>
  <td>' . &error_text('lan_address') . '</td>
</tr>
</table>

<table class="wide">
<tr>
  <td colspan="2">' . &my_radio('lan_dhcp_on', 'on') .
    'Hub is a DHCP server</td>
</tr>
<tr>
  <td class="indent"></td>
  <td>' . &lan_dhcp_stuff . '</td>
</tr>
<tr>
  <td colspan="2">' . &my_radio('lan_dhcp_on', 'off') .
    'Hub is not serving DHCP</td>
</tr>
</table>
';
}

sub lan_dhcp_stuff {
    return '
<table class="wide">
<tr>
  <td>Address range:' .
    &ui_textbox('lan_dhcp_range_start', $in{'lan_dhcp_range_start'}, 3) .
    ' to ' .
    &ui_textbox('lan_dhcp_range_end', $in{'lan_dhcp_range_end'}, 3) .
  '</td>
  <td>' . &error_text('lan_dhcp_range_start') .
    '<br/>' . &error_text('lan_dhcp_range_end') . '
  </td>
</tr>
</table>
';
}

sub hidden_values {
    return '
<input type="hidden" name="lan_dhcp_was_on" value="' . $in{'lan_dhcp_on'} . '">
';
}
