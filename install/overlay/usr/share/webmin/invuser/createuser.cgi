#!/usr/bin/perl
# Either redirects to link.cgi, if a URL has been set, or asks for a URL

require './invuser-lib.pl';
require './validation.pl';
&ReadParse();

$username=$in{'uname'};
$upasswd=$in{'upasswd'};
$upasswd2=$in{'upasswd2'};
$realname="Inveneo User";
$usercreatecmd="/opt/inveneo/bin/inv-user-create.py";

# Return code constants
use constant RET_USER_EXISTS => 9;

	# validate input fields
	&error_setup('Failed to create user');
	$valid_input = 1;
        @errors = ();

	if ( !is_valid_username($username) ) {
		$valid_input = 0;
		push @errors,'The username must start with a letter or number and be greater than 2 characters. The body of the user name must contain only alphanumeric characters or an underscore.';
	}

	if ( $upasswd =~ /^\s*$/ ) {
		$valid_input = 0;
		push @errors,'The password cannot be blank.';
	}
 
	if ( ! ( $upasswd eq $upasswd2 ) ) {
		$valid_input = 0;
		push @errors,'The passwords do not match.';
	}
		
	
	if ( $valid_input ) {
		system "$usercreatecmd -p " . quote_path($upasswd) . " -c \"" . quote_path($realname) . "\" " . quote_path($username);
                $ret_code = $? >> 8;
		if ( $ret_code == RET_USER_EXISTS ) {
			&ui_print_header(undef, "User creation", "", undef, 1, 1);
			&error("The user $username already exists.");	
			&ui_print_footer("/", $text{'index'});
		} elsif ( $ret_code != 0 ) {
			&ui_print_header(undef, "User creation", "", undef, 1, 1);
                        &error('The external process has failed with code ' . $ret);
			&ui_print_footer("/", $text{'index'});
                } else {
			&redirect("index.cgi?msg=" . urlize("The new user '$username' was created.<br>"));
		}
	} else {
               &ui_print_header(undef, "User creation", "", undef, 1, 1);
               &error(generate_error_list(@errors));
	       &ui_print_footer("/", $text{'index'}); 
        }
	

