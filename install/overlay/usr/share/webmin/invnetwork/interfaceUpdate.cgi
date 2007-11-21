#!/usr/bin/perl
# Either redirects to link.cgi, if a URL has been set, or asks for a URL
require './invnetwork-lib.pl';
require '../invlib/form.pm';
require '../web-lib-funcs.pl';
require '../net/debian-linux-lib.pl';
use dhcp;

sub update_interface_static {
	my ( $interface, $options ) = @_; 	
	modify_interface_def($interface,'inet','static',$options, 0);
}

sub update_interface_dhcp {
	my ( $interface ) = @_;
	$options = [ 
		['pre-up', "iptables -t nat -A POSTROUTING -o $interface -j MASQUERADE"],
		['post-down', "iptables -t nat -D POSTROUTING -o $interface -j MASQUERADE"]
	];
		
	modify_interface_def($interface,'inet','dhcp',$options,0);
}



&ReadParse();

$type = lc($in{'type'});
if ( $type eq 'static' ) {
	$iface = $in{'interface'};
	$address = $in{'ip'};
	$mask = $in{'mask'};
	$gateway = $in{'gateway'};
	$dns1 = $in{'dns1'};
	$dns2 = $in{'dns2'};

	#TODO: validate input params

	$options = []; 
	push (@{$options}, ['address', $address]) if ( $address );
	push (@{$options}, ['netmask', $mask]) if ( $mask );
	push (@{$options}, ['gateway', $gateway]) if ( $gateway );

	update_interface_static($iface,$options);
	
	$msg = "The static interface settings for $iface were updated.";
	$redirect = "index.cgi";
} elsif ( $type eq 'dhcp' ) { 
	$iface = $in{'interface'};	
	
	update_interface_dhcp($iface);
	

	$msg = "The interface $iface is configured to use dhcp.";
	$redirect = "index.cgi"; 
} elsif ( $type eq 'ppp' ) {

}

apply_network();

if ( $redirect ) {
	redirect($redirect . (($msg) ? ("?msg=" . urlize($msg)) : ""));
} else {
	&ui_print_header(undef, $module_info{'desc'}, "", undef, 1, 1);     
	print "<h3>$msg</h3>";
	&ui_print_footer("/", $text{'index'});
}


