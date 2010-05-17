#!/usr/bin/perl
# Deletes a user

require './invuser-lib.pl';
&ReadParse();

$username=$in{'user'};
$userdelcmd="/opt/inveneo/bin/inv-user-del.py";

system "$userdelcmd " . quote_path($username);

&redirect("index.cgi?msg=" . urlize("'$username' deleted."));

