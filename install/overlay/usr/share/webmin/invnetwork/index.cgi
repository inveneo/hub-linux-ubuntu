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

print <<JS;
	<script type='text/javascript'>
		function handleSelectChange(sel) {
			if ( sel.selectedIndex>0 ) { 
				sel.form.action = dispatchURL(sel.options[sel.selectedIndex].value); 
				sel.form.submit(); 
			}			
		}
		function dispatchURL(value) {
			var ar = new Array();
			ar['dhcp'] = 'interfaceUpdate.cgi';
			ar['static'] = 'interfaceConfig.cgi';	
			ar['ppp'] = 'interfaceConfig.cgi';
			return ar[value.toLowerCase()];
		} 		
		function deleteStaticDHCP(idx) {
			redirectmsg = 'The static DHCP binding was successfully deleted.'; 
			redirecturl = '../invnetwork/index.cgi';			
			document.location = 
				'../dhcpd/save_host.cgi?' + 
				'delete=Delete&' + 
				'idx=' + idx + '&' + 
				'inveneo_redirect=' + escape(redirecturl) + '&' + 
				'inveneo_message=' + escape(redirectmsg);
		}
	</script>
JS

$interfaces = get_network_interfaces();	
$configTypes = [ ['- Select One -', '- Select One -'], ['DHCP', 'DHCP'], ['Static', 'Static'] ];
print &ui_form_start("interfaceConfig.cgi","post");
print &ui_hidden('interface',WAN_INTERFACE);
print "<h2>WAN Configuration</h2>";
print "<table>";
print_row_title(onchange_select("type", "", $configTypes, "handleSelectChange(this)"));
print "</table>";
print &ui_form_end();

print "<hr>";
$configTypes = [ ['Static', 'Static'] ];
print &ui_form_start("interfaceConfig.cgi","post");
print &ui_hidden('interface',LAN_INTERFACE);
print &ui_hidden('type','Static');
print "<h2>LAN Configuration</h2>";
print "<table>";
print_row_title(onchange_select("", "", $configTypes, ""), "<input type='submit' value='Edit'>");
print "</table>";
print &ui_form_end();

print "<hr>";
$status = get_dhcp_status();
print &ui_form_start("updateDhcpStatus.cgi","get");
print "<h2>DHCP Server</h2>";
print "Server Running? " . &ui_select("status", ($status eq "Enabled") ? "yes" : "no", [ ["yes", "yes"], ["no", "no"] ]);
print "&nbsp;<input type='button' value='Toggle' onclick='this.form.status.selectedIndex = (this.form.status.selectedIndex==0) ? 1 : 0; this.form.submit();'>";
print &ui_form_end();

print "<hr>";

@hosts = get_hosts();
#print "hosts<br><pre>" . Dumper(\@hosts) . "</pre>";

print &ui_form_start("updateDhcpStatus.cgi","get");
print "<h2>Static DHCP Bindings</h2>";
$columns = ["Host Name", "MAC Address","Network Address", "&nbsp;"];
print &ui_columns_start($columns);

foreach $host ( @hosts ) {
	$hardware = find_member($host,'hardware');
	$macAddr = $1 if ($hardware =~ m/(([a-f0-9][a-f0-9]:){5}[a-f0-9][a-f0-9])/i);
	$fAddr = find_member($host,'fixed-address');
	
	if ( $macAddr && $fAddr ) {
		$name = ${ $host }{'value'};
		$index = ${ $host }{'index'};
		print &ui_columns_row([$name,$macAddr,$fAddr,"<a href='javascript:deleteStaticDHCP($index)'>delete</a>"]);
	}
}
print &ui_columns_end();
print &ui_form_end();

print &ui_form_start("../dhcpd/save_host.cgi","post");
print "<h4>Add a new static dhcp binding</h4><table>";

#These are required fields for save_host.cgi
@default_fields = ( 
	'default-lease-time_def', 'max-lease-time_def', 'server-name_def', 
	'dynamic-bootp-lease-length_def', 'dynamic-bootp-lease-cutoff_def', 
	'ddns-domainname_def', 'ddns-rev-domainname_def', 'ddns-hostname_def',
	'next-server_def', 'new', 'inveneo' );
foreach $field ( @default_fields ) {
	print "<input type='hidden' name='$field' value='1'>";
}
print "<input type='hidden' name='hardware_type' value='ethernet'>";
print "<input type='hidden' name='inveneo_redirect' value='../invnetwork/index.cgi'>";
print "<input type='hidden' name='inveneo_message' value='The static DHCP binding addition was successful.'>";
print_row_title("Host Name","<input name='name' value='' size=50>");
print_row_title("MAC Address","<input name='hardware' value='' size=25>");
print_row_title("Network Address","<input name='fixed-address' value='' size=25>");
print_row_title("<input type='submit' value='Add'>");
print "</table>";
print &ui_form_end();

&ui_print_footer("/", $text{'index'});
