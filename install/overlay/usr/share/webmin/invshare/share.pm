# class to handle interacting with samba shares
#
#
require "./util.pl";

use constant SHARE_CONF_DIR => "/etc/inveneo/samba/shares.d";

sub slurp_contents {
    local( $/ );
    my $fn = shift;    
    open (FH,$fn);
    $contents = <FH>;
    close(FH);
    return $contents; 
}

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
    local( $/ );
    my $name = shift;

    if ( -e get_share_conf_filename($name . "_docs") ) {
      #use the users' personal share
      $fn = get_share_conf_filename($name . "_docs");     
    } else {
      $fn = get_share_conf_filename($name);
    }
    
    $contents = slurp_contents($fn);    

    if ( $contents =~ m/valid users\s*=(.+)/ ) {
        return trim($1);
    } else {        
        return "Public";
    }
}

sub is_valid_share_name { 
   my $name = shift;
   return ( $name =~ /^(\w| )+$/ );  
}

sub convert_to_share_dir_name { 
   my $name = trim(lc(shift)); 
   return $name;
}

sub share_exists {    
   my $name = shift; 
   if ( is_valid_share_name($name) ) { 
      my $conf_fn = get_share_conf_filename($name);    

      # test for the user's personal share
      my $conf_fn2 = get_share_conf_filename($name . "_docs");
      return (( -e "$conf_fn" ) || ( -e "$conf_fn2")) ? 1 : 0; 
   } else {
      return 0;
   } 
}

sub get_users_list { 
    $cmd = "pdbedit -w -L | awk -F: '{print \$1\":\"\$2}'";    
    open(IN, "$cmd |") or die "Error executing $cmd";

    my $uidCount = 0; 
    my @uid = ();
    my @uidNum = ();

    while ($line = <IN>) {
       chomp $line;
       ($lineUid,$lineUidNumber) = split(/:/,$line);
       $uidCount++;
       $uid[$uidCount]=$lineUid;
       $uidNum[$uidCount]=$lineUidNumber;
    }
        
    my @retList = (); 
    my $cnt = 0; 
    while ( $cnt < $uidCount ) {
        if ( ($uidNum[$cnt] > 1400) && ($uidNum[$cnt] < 65000) ) {
           my @userInfo = ( $uidNum[$cnt], $uid[$cnt] );
           push @retList, \@userInfo;
        }
        $cnt++;
    } 

    return \@retList;

}

sub reload_samba_settings { 
    
    local( $/ );

    system("/etc/init.d/samba-shares.sh start");

    open (FH,"/etc/init.d/samba reload |");
    $result = <FH>;
    close(FH);
    
    if ( $result =~ m/No process in pidfile/ ) {
       system("/etc/init.d/samba start");
    } 
     
}

sub get_share_conf_filename {
    my $name = shift;
    $conf_fn = SHARE_CONF_DIR . "/" . convert_to_share_dir_name($name) . ".conf";
    return $conf_fn;
}



sub delete_share {
    my $sharename = shift;
    if ( is_valid_share_name($sharename) ) {
        $conf_fn = get_share_conf_filename($sharename);
        if ( !unlink(get_share_conf_filename($sharename)) ) {
           # delete the user's personal share
	   return unlink(get_share_conf_filename($sharename . "_docs"));
	} else {
	   return 1;        
	}
    } else {
	return 0;
    }
}

1;
