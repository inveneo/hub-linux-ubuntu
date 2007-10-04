#!/usr/bin/perl
# Either redirects to link.cgi, if a URL has been set, or asks for a URL

require './invuser-lib.pl';
&ReadParse();

$username=$in{'uname'};
$upasswd=$in{'upasswd'};
$userpwresetcmd="/opt/inveneo/bin/inv-passwd.py";

# Ask for Username and password
	&ui_print_header(undef, "Password Reset", "", undef, 1, 1);
	print "Setting password for $username....";

	system "$userpwresetcmd -u $username -p $upasswd";

	print "done<br>";
	&ui_print_footer("/", $text{'index'});

