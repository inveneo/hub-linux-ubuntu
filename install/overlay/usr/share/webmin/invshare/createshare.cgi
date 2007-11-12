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

$sharename=trim($in{'sharename'});
$public=trim($in{'public'});
$owner=trim($in{'owner'});

	# validate input fields
	&error_setup('Failed to create user');
	$valid_input = 1;
        @errors = ();

	if ( !is_valid_share_name($sharename) ) {
	    $valid_input = 0;
	    push @errors,'The share name must not be blank and can only contain alpha-numeric characters and a space.';
	} 
        
        if ( share_exists($sharename) ) {
            $valid_input = 0;
            push @errors, "The share '$sharename' already exists.";
        } 

        $share_conf = get_share_conf_filename($sharename); 

	if ( $valid_input ) {            
            
            if ( $public ) {
              $data_file= SHARE_TEMPLATE_DIR . "public.conf";
              $cmd = "sed \"s/\%SHARENAME\%/$sharename/g\" \"$data_file\" > \"$share_conf\"";
              mkdir(SHARE_STORAGE_PUB_DIR . convert_to_share_dir_name($sharename));
              system($cmd);              
            } else {
              $data_file = SHARE_TEMPLATE_DIR . "private.conf";             
              $cmd = "sed \"s/\%SHARENAME\%/$sharename/g;s/\%USERNAME\%/$owner/g\" \"$data_file\" > \"$share_conf\"";
              mkdir(SHARE_STORAGE_PRI_DIR . convert_to_share_dir_name($sharename));
              system($cmd);             
            }
            
            $res = $? >> 8;
            if ( $res != 0 ) {
                &error("Error $res while creating the share.");
            } else {
                reload_samba_settings();
                redirect("index.cgi?msg=The share '$sharename' was successfully created.");
            }

	} else {

            &ui_print_header(undef, "Share creation", "", undef, 1, 1);
            &error(generate_error_list(@errors));
            &ui_print_footer("/", $text{'index'}); 

        }
	

