#!/usr/bin/perl
# Deletes a user

require './invuser-lib.pl';
&ReadParse();

$username=$in{'user'};
$userdelcmd="/opt/inveneo/bin/invuserdel";

&ui_print_header(undef, "User removal", "", undef, 1, 1);
print "Deleting user: " . $username ." ... ";

system "$userdelcmd $username";

print "done<br>";
&ui_print_footer("/", $text{'index'});

