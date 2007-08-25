#!/usr/bin/perl
# Either redirects to link.cgi, if a URL has been set, or asks for a URL

require './invuser-lib.pl';
if ($config{'url'}) {
	&redirect("link.cgi/$config{'url'}");
	}
else {
	# Ask for Username and password
	&ui_print_header(undef, $module_info{'desc'}, "", undef, 1, 1);

	# List existing users
	$cmd = "ldapsearch -x  -LLL \"(objectClass=sambaSamAccount)\" uidNumber uid | grep \"^uid\" |  tr -d \":\"";

	open(IN, "$cmd |") or die "Error executing $cmd";

	$uidCount=0;
	$uidNumberCount=0;
	while ($line = <IN>) {
		chomp $line;
		($attrib,$value) = split(/ /,$line);
		if ($attrib eq "uid") {
			$uidCount++;
			$uid[$uidCount]=$value;
		}
		if ($attrib eq "uidNumber") {
			$uidNumberCount++;
			$uidNumber[$uidNumberCount]=$value;
		}
	}

	@userlisttable = ("Username", "Edit", "Delete");
	print "<h2>User list</h2>\n";
	print &ui_columns_start(\@userlisttable);
	for ($i=1; $i<= $uidCount; $i++) {
		if ($uidNumber[$i] > 9999) {
			$column1 = $uid[$i] . "(" . $uidNumber[$i] . ")";
			$column2 = "<a href='changepwuser.cgi?user=" . $uid[$i] . "'>Reset Password</a>";
			$column3 = "<a href='deluser.cgi?user=" . $uid[$i] . "'>Delete</a>";
			@usertablerow = ($column1, $column2, $column3);
			print &ui_columns_row(\@usertablerow);
		}
	}
	print &ui_columns_end();
	print "<br>\n";
	print "<h2>Add new user</h2>\n";
	print &ui_form_start("createuser.cgi");
	print "<b>Username</b>\n";
	print &ui_textbox("uname", undef, 32),"\n";
	print "<b>Password</b>\n";
	print &ui_textbox("upasswd", undef, 32),"\n";
	print &ui_submit("Create"),"\n";
	print &ui_form_end();
	&ui_print_footer("/", $text{'index'});
	}

