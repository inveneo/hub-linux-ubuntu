#!/usr/bin/perl
# Either redirects to link.cgi, if a URL has been set, or asks for a URL

require './invuser-lib.pl';
&ReadParse();

$username=$in{'user'};
$usercreatecmd="/opt/inveneo/bin/inv-user-create.py";

#print "<h2>Add new user</h2>\n";

# Ask for Username and password
	&ui_print_header(undef, "Password Reset", "", undef, 1, 1);

	print &ui_form_start("changepwuser2.cgi");
	print "<b>Set new password for $username</b><br>\n";
        
	print "New password: ",&ui_password("upasswd", undef, 32),"<br>\n";
	print "New password(again): ",&ui_password("upasswd2", undef, 32),"<br>\n";
	print &ui_hidden("uname", $username),"\n";
	print &ui_submit("Submit"),"\n";
	print &ui_form_end();

	&ui_print_footer("/", $text{'index'});

