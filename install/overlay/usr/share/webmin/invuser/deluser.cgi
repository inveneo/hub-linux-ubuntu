#!/usr/bin/perl
# Deletes a user

require './invuser-lib.pl';
&ReadParse();

$username=$in{'user'};
$userdelcmd="/opt/inveneo/bin/inv-user-del.py";

&ui_print_header(undef, "User removal", "", undef, 1, 1);
print "Deleting user: " . $username ." ... ";

system "$userdelcmd " . quote_path($username);

print "done<br>";
&ui_print_footer("/", $text{'index'});

