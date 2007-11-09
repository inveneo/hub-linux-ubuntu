# class to handle interacting with samba shares
#
#
require "./util.pl";

use constant SHARE_CONF_DIR => "/etc/inveneo/samba/shares.d";

sub get_share_names {
    my $share_dir = shift; 

    @files = glob($share_dir . "/*.conf");
    my @found_shares = ();  

    foreach $file (@files) {
       open(FILE, $file) || die("Could not open file!");
       @file_data=<FILE>; 
       foreach $line (@file_data) {
           if ( $line =~ /\[(.*)\]/) { 
              $value = trim($1); 
              push @found_shares, $value;
              break;
           }
       }

       close(FILE);
    }

    return @found_shares;

}

sub get_share_owner { 
        return "Public";   
}

sub is_valid_share_name { 
   my $name = shift;
   return ( $name =~ /^(\w| )+$/ );  
}

sub convert_to_share_dir_name { 
   my $name = lc(shift); 
   $name =~ s/ /\^/g;
   return $name;
}

sub share_exists { 
   my $name = shift; 
   if ( is_valid_share_name($name) ) { 
      $conf_fn = SHARE_CONF_DIR . "/" . convert_to_share_dir_name($name) . ".conf";
      ( -e $conf_fn ) ? 1 : 0; 
   } else {
      return 0;
   } 
}

1;
