#!/usr/bin/perl
# Either redirects to link.cgi, if a URL has been set, or asks for a URL

require './invuser-lib.pl';
require '../invlib/validation.pl';
&ReadParse();

$username=$in{'uname'};
$upasswd=$in{'upasswd'};
$upasswd2=$in{'upasswd2'};
$userpwresetcmd="/opt/inveneo/bin/inv-passwd.py";

# Validate Input
@errors = ();
$valid_input = 1;

if ( is_blank($upasswd) ) {
    $valid_input = 0;
    push @errors, 'The password cannot be blank.';
}

if ( ! ( $upasswd eq $upasswd2 ) ) {
    $valid_input = 0;
    push @errors,'The passwords do not match.';
}

if ( $valid_input ) { 
    &ui_print_header(undef, "Password Reset", "", undef, 1, 1);
    print "Setting password for $username....";

    system "$userpwresetcmd -u " . quote_path($username) . " -p " . quote_path($upasswd);

    print "done<br>";
    &ui_print_footer("/", $text{'index'});
} else { 
    &error(generate_error_list(@errors));
}
