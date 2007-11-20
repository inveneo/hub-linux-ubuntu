#!/usr/bin/perl
do '../web-lib.pl';
require "../invshare/invshare-lib.pl";

$server = $ENV{'SERVER_NAME'};
$port = 8008;

&redirect("http://$server:$port/");

#use Data::Dumper;
#&ui_print_header(undef, $module_info{'desc'}, "", undef, 1, 1);
#print "<pre>" . Dumper(\%ENV) . "</pre>";
#print "http://$server:$port/";
#&ui_print_footer("/", $text{'index'});
