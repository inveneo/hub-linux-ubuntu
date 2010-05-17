#!/usr/bin/perl
# Either redirects to link.cgi, if a URL has been set, or asks for a URL
require './invraidnotify-lib.pl';
require '../invlib/validation.pl';
use raidalertconfig; 
&ReadParse();

sub validate_input {
        my $configFileMap = shift;
        my @errors = (); 
        my %nameTranslation = (
                MONITOR_SMTP_USERNAME => "SMTP Username",
                MONITOR_SMTP_PASSWORD => "SMTP Password",
                MONITOR_SMTP_HOSTNAME => "SMTP Hostname",
                MONITOR_SMTP_PORT => "SMTP Port",
                MONITOR_SMTP_TLS => "Secure Connection", 
                MONITOR_SMTP_SENDER => "From Address", 
                MONITOR_SMTP_DEFAULT_MESSAGE => "Message", 
                MONITOR_SMTP_DEFAULT_SUBJECT => "Subject",
                MONITOR_SMTP_RECIPIENT => "To Address"
            ); 

        if ( ! ($configFileMap->{"MONITOR_SMTP_PORT"}=~m/\d+/) ) {
            push(@errors,"SMTP Port must be a number.");
            $configFileMap->{"MONITOR_SMTP_PORT"} = "25";
        }

        my @should_not_be_blank = (
                "MONITOR_SMTP_HOSTNAME",
                "MONITOR_SMTP_SENDER", 
                "MONITOR_SMTP_RECIPIENT",
                "MONITOR_SMTP_DEFAULT_SUBJECT"
        );

        foreach ( @should_not_be_blank ) {
            $key = $_;
            push(@errors,"The " . $nameTranslation{$key} . " field cannot be blank.") if is_blank($configFileMap->{$key});   
        }

        if ( $configFileMap->{"SMTP_REQUIRES_AUTHENTICATION"} eq 1 ) {
            $key = "MONITOR_SMTP_USERNAME";
            push(@errors,"The " . $nameTranslation{$key} . " field cannot be blank.") if is_blank($configFileMap->{$key});
            $key = "MONITOR_SMTP_PASSWORD";
            push(@errors,"The " . $nameTranslation{$key} . " field cannot be blank.") if is_blank($configFileMap->{$key});
        }

        return @errors;
}

my @errors;
my $configFileMap;
my $msg = $in{'msg'};
my @items = ( 
    "MONITOR_SMTP_USERNAME", "MONITOR_SMTP_PASSWORD", "MONITOR_SMTP_HOSTNAME",
    "MONITOR_SMTP_PORT", "MONITOR_SMTP_TLS", "MONITOR_SMTP_SENDER", 
    "MONITOR_SMTP_DEFAULT_MESSAGE", "MONITOR_SMTP_DEFAULT_SUBJECT", "MONITOR_SMTP_RECIPIENT", "SMTP_REQUIRES_AUTHENTICATION" );

&ui_print_header(undef, $module_info{'desc'}, "", undef, 1, 1);
print <<END;
<script type='text/javascript'> 
        function change_disabled(fields,state) {
                for ( var idx=0; idx<fields.length; idx++ ) {
                        fields[idx].disabled = state;
                }
        } 
        function handle_auth_changed(element) {
                var state;
                var disabledFields = new Array();
                disabledFields[0] = element.form.elements.MONITOR_SMTP_USERNAME;
                disabledFields[1] = element.form.elements.MONITOR_SMTP_PASSWORD;
                //disabledFields[2] = element.form.elements.MONITOR_SMTP_TLS;

                if ( element.checked ) {
                    state = false;
                } else {
                    state = true;
                }
                change_disabled(disabledFields,state);
        }
</script> 
END


# read the form vaules
if ( defined $in{'form_post'} ) {
        #insert items from the http request into the map
        for $key (@items) {
                $configFileMap->{$key} = $in{$key};
        }
        @errors = validate_input($configFileMap);
        if ( @errors > 0 ) {
                for $str (@errors) {
                        print "<p><font color='#ff0000'>- $str</font>";
                }
                print "<br><br>";
        } else {
                # default flag values if not set 
                $configFileMap->{"SMTP_REQUIRES_AUTHENTICATION"} = "0" if !defined($configFileMap->{"SMTP_REQUIRES_AUTHENTICATION"});
                $configFileMap->{"MONITOR_SMTP_TLS"} = "0" if !defined($configFileMap->{"MONITOR_SMTP_TLS"});
                #save the changed settings
                write_config_data($configFileMap);
        }
} else {
        #read the map values from the config file
        $configFileMap = read_config_items(@items); 
}


#print the form

        print "<h2>Raid Notification Configuration</h2>";
        print &ui_form_start("index.cgi");
        print "<input type='hidden' name='form_post' value='1'></input>";
        print "<table>";
        print "<tr><td><h4>Server Configuration</h4></td></tr>";
        input_box_row("MONITOR_SMTP_HOSTNAME","SMTP Host",$configFileMap->{"MONITOR_SMTP_HOSTNAME"});
        input_box_row("MONITOR_SMTP_PORT","SMTP Port",$configFileMap->{"MONITOR_SMTP_PORT"});
        print_row_title("&nbsp;","&nbsp;");

        my $smtp_auth = $configFileMap->{"SMTP_REQUIRES_AUTHENTICATION"} eq 1 ? "checked" : "";
        print_row_title("Use Secure Connection?", "<input name='MONITOR_SMTP_TLS' type='checkbox' value='1' " . ($configFileMap->{"MONITOR_SMTP_TLS"} eq "1" ? 'checked' : '') . "></input>");
        print_row_title("&nbsp;","&nbsp;");

        print_row_title("Server requires authentication:","<input $smtp_auth name='SMTP_REQUIRES_AUTHENTICATION' value='1' type='checkbox' onchange='handle_auth_changed(this);'/></input>");
        input_box_row("MONITOR_SMTP_USERNAME","SMTP User Name",$configFileMap->{"MONITOR_SMTP_USERNAME"});
        print_row_title("SMTP Password","<input name='MONITOR_SMTP_PASSWORD' type='password' size='32' value='" . $configFileMap->{"MONITOR_SMTP_PASSWORD"} . "'></input>");
        print_row_title("&nbsp;","&nbsp;");

        print "<tr><td><h4>Message Contents</h4></td></tr>";
        input_box_row("MONITOR_SMTP_SENDER","From Address",$configFileMap->{"MONITOR_SMTP_SENDER"});
        input_box_row("MONITOR_SMTP_RECIPIENT","To Address",$configFileMap->{"MONITOR_SMTP_RECIPIENT"});
        input_box_row("MONITOR_SMTP_DEFAULT_SUBJECT","Subject",$configFileMap->{"MONITOR_SMTP_DEFAULT_SUBJECT"});
        print_row_title("Message",sprintf("<textarea name='MONITOR_SMTP_DEFAULT_MESSAGE' rows='5' cols='80'>%s</textarea>",$configFileMap->{"MONITOR_SMTP_DEFAULT_MESSAGE"}));

        print "<tr><td colspan='2'>" . &ui_submit("Update Settings") . "</td></tr>";
        print "</table>"; 
        print &ui_form_end();
        
        # update the disabled state of name and pw fields based on the config file.
        print "<script type='text/javascript'>handle_auth_changed(document.forms[0].elements.SMTP_REQUIRES_AUTHENTICATION);</script>";
        &ui_print_footer("/", $text{'index'});
