#!/usr/bin/perl
# Either redirects to link.cgi, if a URL has been set, or asks for a URL

require './invuser-lib.pl';
&ReadParse();

$username=$in{'uname'};
$upasswd=$in{'upasswd'};
$upasswd2=$in{'upasswd2'};
$realname="Inveneo User";
$usercreatecmd="/opt/inveneo/bin/inv-user-create.py";

	sub is_valid_username {
		my $val = shift;
		return !( $val =~ /\W+/ ) && !( $val =~ /^\s*$/ ); 
	}
	
	# validate input fields
	&error_setup('Failed to create user.');
	$valid_input = true;
	if ( !is_valid_username($username) ) {
		&error('The username must contain only alpha-numeric characters and an underscore.');
		$valid_input = false;
	}

	if ( $upasswd =~ /^\s*$/ ) {
		&error('The password cannot be blank.');
		$valid_input = false;
	}
 
	if ( ! ( $upasswd eq $upasswd2 ) ) {
		&error('The passwords do not match.');
		$valid_input = false;
	}
		
	&ui_print_header(undef, "User creation", "", undef, 1, 1);
	if ( $valid_input == true ) {

		print "Creating user: " . $in{'uname'} ." with password " . $in{'upasswd'} . "....";
	
		system "$usercreatecmd -p " . quote_path($upasswd) . " -c \"" . quote_path($realname) . "\" " . quote_path($username);
		
		print "done<br>";
	
	} 
	&ui_print_footer("/", $text{'index'});

