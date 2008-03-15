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

        for $key ( keys(%$configFileMap) ) {
            if ( !($key eq 'MONITOR_SMTP_TLS') ) {
            push(@errors,"The " . $nameTranslation{$key} . " field cannot be blank.") if length($configFileMap->{$key}) eq 0;   
            }
        }

        return @errors;
}

my @errors;
my $configFileMap;
my $msg = $in{'msg'};
my @items = ( 
    "MONITOR_SMTP_USERNAME", "MONITOR_SMTP_PASSWORD", "MONITOR_SMTP_HOSTNAME",
    "MONITOR_SMTP_PORT", "MONITOR_SMTP_TLS", "MONITOR_SMTP_SENDER", 
    "MONITOR_SMTP_DEFAULT_MESSAGE", "MONITOR_SMTP_DEFAULT_SUBJECT", "MONITOR_SMTP_RECIPIENT" );

&ui_print_header(undef, $module_info{'desc'}, "", undef, 1, 1);

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
        input_box_row("MONITOR_SMTP_USERNAME","SMTP User Name",$configFileMap->{"MONITOR_SMTP_USERNAME"});
        printf("<tr><td><b>SMTP Password</b><td><input name='MONITOR_SMTP_PASSWORD' type='password' size='32' value='%s'></input></td></tr>", $configFileMap->{"MONITOR_SMTP_PASSWORD"});
        input_box_row("MONITOR_SMTP_HOSTNAME","SMTP Host",$configFileMap->{"MONITOR_SMTP_HOSTNAME"});
        input_box_row("MONITOR_SMTP_PORT","SMTP Port",$configFileMap->{"MONITOR_SMTP_PORT"});
        printf("<tr><td><b>Use Secure Connection?</b></td><td><input name='MONITOR_SMTP_TLS' type='checkbox' value='1' %s></input></td></tr>",$configFileMap->{"MONITOR_SMTP_TLS"} eq "1" ? 'checked' : '');
        print "<tr><td><h4>Message Contents</h4></td></tr>";
        input_box_row("MONITOR_SMTP_SENDER","From Address",$configFileMap->{"MONITOR_SMTP_SENDER"});
        input_box_row("MONITOR_SMTP_RECIPIENT","To Address",$configFileMap->{"MONITOR_SMTP_RECIPIENT"});
        printf("<tr><td><b>Subject</b></td><td><input name='MONITOR_SMTP_DEFAULT_SUBJECT' size='80' value='%s'></input></td></tr>", $configFileMap->{"MONITOR_SMTP_DEFAULT_SUBJECT"});
        printf("<tr><td><b>Message</b></td><td><textarea name='MONITOR_SMTP_DEFAULT_MESSAGE' rows='5' cols='80'>%s</textarea></td></tr>", $configFileMap->{"MONITOR_SMTP_DEFAULT_MESSAGE"});
        print "<tr><td colspan='2'>" . &ui_submit("Update Settings") . "</td></tr>";
        print "</table>"; 
        print &ui_form_end();

        &ui_print_footer("/", $text{'index'});
