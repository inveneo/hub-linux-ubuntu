#!/usr/bin/perl
# Either redirects to link.cgi, if a URL has been set, or asks for a URL

require './invuser-lib.pl';
&ReadParse();

$username=$in{'uname'};
$upasswd=$in{'upasswd'};
$realname="Inveneo User";
$usercreatecmd="/opt/inveneo/bin/inv-user-create.py";

# Ask for Username and password
	&ui_print_header(undef, "User creation", "", undef, 1, 1);
	print "Creating user: " . $in{'uname'} ." with password " . $in{'upasswd'} . "....";

	system "$usercreatecmd -p $upasswd -c \"$realname\"  $username ";

	print "done<br>";
	&ui_print_footer("/", $text{'index'});

