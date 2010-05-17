#!/usr/bin/perl
do '../web-lib.pl';
require "../invshare/invshare-lib.pl";

sub not_blank {
    my($var) = @_;
    return true if (defined($var) && !($var =~ m/^\s*$/)); 
}

sub print_href {
    my($name,$id,$url,$desc,$target) = @_;
    print "<a ";
    print "name='$name' " if not_blank($name);
    print "id='$id' " if not_blank($id); 
    print "target='$target' " if not_blank($target);
    print "href='$url' " if not_blank($url);
    print ">"; 
    if ( not_blank($desc) ) { 
        print $desc;
    } else {
        print $url;
    } 
    print "</a>";
}


$server = $ENV{'SERVER_NAME'};
$port = 8088;

&ReadParse();

if ($config{'url'}) {
	&redirect("link.cgi/$config{'url'}");
	}
else {
	# Ask for Username and password
	&ui_print_header(undef, $module_info{'desc'}, "", undef, 1, 1);
	
	$msg = $in{'msg'};
	if ( $msg ) {
		print "<h4>" . un_urlize($msg) . "</h4><br>";
	}
        
         
        $initial_setup_url = "http://$server:$port/asterisk/static/config/setup/install.html";
        $config_url = "http://$server:$port/asterisk/static/config/cfgbasic.html";

	print "<h2>Asterisk Management</h2>\n";
        #print "<p><br>";
        #print_href(undef,undef,$initial_setup_url,"Initial Asterisk Configuration","_asterisk_");
        #print "&nbsp;&nbsp; | &nbsp;&nbsp;";
        print_href(undef,undef,$config_url,"Asterisk Configuration","_asterisk_");
        
	&ui_print_footer("/", $text{'index'});
    }
