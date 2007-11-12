#!/usr/bin/perl
# Either redirects to link.cgi, if a URL has been set, or asks for a URL
use share;
require './invshare-lib.pl';
require './validation.pl';
&ReadParse();

use constant SHARE_CONF_DIR => "/etc/inveneo/samba/shares.d/";
use constant SHARE_TEMPLATE_DIR => "/opt/inveneo/skeleton/samba/";
use constant SHARE_STORAGE_PUB_DIR => "/srv/samba/public_shares/";
use constant SHARE_STORAGE_PRI_DIR => "/srv/samba/user_shares/";

$sharename=$in{'sharename'};

	# validate input fields
	&error_setup('Failed to create user');
	$valid_input = 1;
        @errors = ();

	

	if ( !is_valid_share_name($sharename) ) {
		$valid_input = 0;
		push @errors,"The share '$sharename' is not valid.";
	} 

        if ( !share_exists($sharename) ) {
                $valid_input = 0;
                push @errors,"The share '$sharename' does not exist.";              
        }

	if ( $valid_input ) {
            if ( delete_share($sharename) ) {
                reload_samba_settings();
                &redirect("index.cgi?msg=" . urlize("The share '$sharename' was deleted."));                    
            }
	} else {
            &ui_print_header(undef, "Delete Share", "", undef, 1, 1);
	    &error(generate_error_list(@errors)); 
	    &ui_print_footer("/", $text{'index'});            
        }
	

