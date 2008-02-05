#!/usr/bin/perl
do '../web-lib.pl';
#require "../invshare/invshare-lib.pl";

$server = $ENV{'SERVER_NAME'};
$port = 631;
&redirect("http://$server:$port/");

