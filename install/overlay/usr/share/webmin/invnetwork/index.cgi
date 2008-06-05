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

function changeDisplay(the_div,the_change) {
    var the_style = getStyleObject(the_div);
    if (the_style != false) {
        the_style.display = the_change;
    }
}

function hideAll() {
    changeDisplay("eth0_stuff","none");
    changeDisplay("modem_stuff","none");
    changeDisplay("eth1_stuff","none");
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
    print &ui_form_end();
}

sub host_stuff {
    return '
<table class="wide">
<tr>
  <td class="label">Hostname:</td>
  <td class="entry">
    <input name="hostname" value="' . $in{'hostname'} . '" size="20">
  </td>
  <td align="left">' . &error_text('hostname') . '</td>
</tr>
</table>
';
}

sub wan_stuff {
    return '
<h2>Connection to the Internet</h2>
<table class="wide">
<tr>
  <td colspan="3">' . &error_text('wan_interface') . '</td>
</tr>
<tr>
  <td>
    <input type="radio" name="wan_interface" value="eth0"
      checked="checked"
      onClick="hideAll(); changeDisplay(\'eth0_stuff\', \'block\');">
      Connected to Internet via WAN Port
    <div id="eth0_stuff" style="margin-left:30px;display:block">' .
      &eth0_stuff . '
    </div>
  </td>
</tr>
<tr>
  <td>
    <input type="radio" name="wan_interface" value="modem"
      onClick="hideAll(); changeDisplay(\'modem_stuff\', \'block\');">
      Connected to Internet via Modem
    <div id="modem_stuff" style="margin-left:30px;display:block">' .
        &modem_stuff . '
    </div>
  </td>
</tr>
<tr>
  <td>
    <input type="radio" name="wan_interface" value="eth1"
      onClick="hideAll(); changeDisplay(\'eth1_stuff\', \'block\');">
      Connected to Internet via Local Network
    <div id="eth1_stuff" style="margin-left:30px;display:block">
      <table class="wide">
        <tr>
          <td class="label">Gateway:<br/><i>optional</i></td>
          <td class="entry">
            <input name="lan_gw" size="20" value="' . $in{'lan_gw'} . '">
          </td>
          <td align="left">' . &error_text('hostname') . '</td>
        </tr>
      </table>
    </div>
  </td>
</tr>
</table>

<table class="wide">
<tr>
  <td class="label">DNS Server(s):<br/>
    <i>optional, separated by spaces</i></td>
  <td class="entry">
    <input name="dns_servers" value="' . $in{'dns_servers'} . '" size="40">
  </td>
  <td align="left">' . &error_text('dns_servers') . '</td>
</tr>
</table>
';
}

sub eth0_stuff {
    return '
<table class="wide">
<tr><td>' . &error_text('wan_method') . '</td></tr>
<tr>
  <td>' . &ui_radio_table('wan_method', $in{'wan_method'},
        [ ['dhcp',   'DHCP Client', '&nbsp'],
          ['static', 'Static', &eth0_static_stuff] ]) . '
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

sub lan_stuff {
    return '
<h2>Connection to Local Network</h2>
<table class="wide">
<tr>
  <td class="label">Hub&apos;s fixed IP address:</td>
  <td>' . &ui_textbox('lan_address', $in{'lan_address'}, 20) . '</td>
  <td>' . &error_text('lan_address') . '</td>
</tr>
</table>
<table class="wide">
<tr>
  <td>
    <input type="radio" name="lan_dhcp_on" value="on" checked="checked">
      Hub is a DHCP server
    <div id="dhcp_on" style="margin-left:30px;display:block">
      <table class="wide">
        <tr>
          <td colspan="2">
            Address range: ' .
            &ui_textbox('lan_dhcp_range_start', $in{'lan_dhcp_range_start'}, 3).
            ' to ' .
            &ui_textbox('lan_dhcp_range_end', $in{'lan_dhcp_range_end'}, 3) . '
          </td>
          <td>' .
          &error_text('lan_dhcp_range_start') .
          &error_text('lan_dhcp_range_end') . '
          </td>
        </tr>
      </table>
    </div>
  </td>
</tr>
<tr>
  <td>
    <input type="radio" name="lan_dhcp_on" value="off">
      Hub is not serving DHCP
    <div id="dhcp_off" style="margin-left:30px;display:block">
    </div>
  </td>
</tr>
</table>
<input type="hidden" name="lan_dhcp_was_on" value="' . $in{'lan_dhcp_on'} . '">
';
}
