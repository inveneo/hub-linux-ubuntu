#!/usr/bin/perl
do '../web-lib.pl';
require "../invshare/invshare-lib.pl";

$server = $ENV{'SERVER_NAME'};
$port = 8008;

&redirect("http://$server:$port/");
