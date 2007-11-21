#!/usr/bin/perl
require './invnetwork-lib.pl';
require '../invlib/form.pm';
require '../invlib/validation.pl';
use dhcp;
&ReadParse();
@errors = ();
$type = uc($in{'type'});
$interface = $in{'interface'};

&error_setup('Update failed');

if ( $type eq 'STATIC' ) {
	&ui_print_header(undef, $module_info{'desc'}, "", undef, 1, 1);
	print "<h2>WAN configuration - $type</h2>";
	print "<table>";
	%values = get_interface_info($interface);
	print &ui_form_start("interfaceUpdate.cgi","post");
	print &ui_hidden('type',$type);
	print &ui_hidden('interface',$interface);
	print_row_title("Interface", $interface);
	print_row_title("IP Address", &ui_textbox("ip",$values{'address'},20));
	print_row_title("Netmask", &ui_textbox("mask",$values{'netmask'},20));
	print_row_title("Gateway", &ui_textbox("gateway",$values{'gateway'},20));
	print_row_title("Preferred DNS", &ui_textbox("dns1",$values{'dns'}[0],20));
	print_row_title("Alternate DNS", &ui_textbox("dns2",$values{'dns'}[1],20));
	print_row_title("", "<input type='submit' value='Update'>");
	print &ui_form_end();
	print "</table>";
	&ui_print_footer("/", $text{'index'});
} elsif ( $type eq 'DHCP' ) {
	$res = enable_dhcp($interface);
	if ( $res ) {
		redirect('index.cgi?msg=' . urlize("DHCP enabled for interface $interface"));			
  	} else {
		push @errors, "An error occured while updating the configuration for $interface";			
	}
} elsif ( $type eq 'PPP' ) { 
	# need more info for this one 	
} else {
	push @errors, "An unknown type was provided.";	
} 

if ( scalar(@errors) > 0 ) { &error(generate_error_list(@errors)); }


