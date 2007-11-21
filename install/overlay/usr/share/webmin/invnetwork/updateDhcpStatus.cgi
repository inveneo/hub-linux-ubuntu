#!/usr/bin/perl

require './invnetwork-lib.pl';
require '../invlib/validation.pl';
use dhcp;
&ReadParse();

$status = $in{'status'};
$action = ($status eq 'no') ? "stop" : "start";

if ( system("/etc/init.d/dhcp3-server $action") == 0 ) {
   	redirect("index.cgi?msg=" . urlize('The DCHP server was ' . (($action eq 'start') ? "started" : "stopped")) . ".");
} else {
        @errors = ( "The command failed with error code $?" );
   	&ui_print_header(undef, "Dhcp Server", "", undef, 1, 1);
        &error(generate_error_list(@errors));
        &ui_print_footer("/", $text{'index'});
}

