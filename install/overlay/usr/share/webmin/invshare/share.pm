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

sub get_users_list { 
    
    $cmd = "ldapsearch -x  -LLL \"(objectClass=sambaSamAccount)\" uidNumber uid | grep \"^uid\" |  tr -d \":\""; 
    open(IN, "$cmd |") or die "Error executing $cmd";

    my $uidCnt = 0; 
    my $uidNumCnt = 0;
    my @uid = ();
    my @uidNum = ();

    while ($line = <IN>) {
       chomp $line;
       ($attr,$val) = split(/ /,$line);
       if ( $attr eq 'uid' ) {
           $uid[$uidCnt++] = $val;
       } elsif ( $attr eq 'uidNumber' ) {
           $uidNum[$uidNumCnt++] = $val;
       }
    }
        
    my @retList = (); 
    my $cnt = 0; 
    while ( $cnt < $uidCnt ) {
        if ( $uidNum[$cnt] > 10000 ) {
           my @userInfo = ( $uidNum[$cnt], $uid[$cnt] );
           push @retList, \@userInfo;
        }
        $cnt++;
    } 

    return \@retList;

}

sub reload_samba_settings { 
    
    local( $/ ) ;

    system("/etc/init.d/samba-shares.sh start");

    open (<FH>,"/etc/init.d/samba reload |");
    $result = <FH>;
    if ( $result =~ m/No process in pidfile/ ) {
       # stopeed here  
    }
     
}

1;
