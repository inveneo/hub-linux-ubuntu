use constant RAID_MONITOR_CONF => "/etc/inveneo/conf.d/raid_monitor.conf";
use constant TEMP_CONFIG_FILE => "/tmp/x.conf";

my $raid_monitor_config = RAID_MONITOR_CONF;

# sets the filename to use as an input source 
sub set_raid_config_file {
       my ( $fn ) = @_;
       $raid_monitor_config = $fn;
       return $fn; 
}

# input: accepts a list of configuration items to be returned
# output: returns a hash of key/value pairs containing the values from the configuration file
sub read_config_items {

        my (@item_names) = @_; 
        my %config_values = ();
	
        $configFileData = read_whole_file($raid_monitor_config);        

	for my $item (@item_names) {
                $config_values{ $item } = get_item_value($item,$configFileData); 
    	}

        return \%config_values;

}

# input: the name of the value we are interested in getting and the config files as an array of lines
# output: the value of the item we are interested in
sub get_item_value {
        my ($name, $configFileData) = @_;
        for my $line (@$configFileData) {
                ($key, $value) = return_key_value_from_input_line($name,$line);
                return $value if defined($value);
        }
        return undef; 
}

# if the line has a 'KEY=VALUE' or 'KEY="VALUE"' format the function will return a 2-tuple containing the key and value.
sub return_key_value_from_input_line {
        my ($name, $line) = @_;
        $name = ".*" if !defined($name);
        if ( $line =~ m/\s*($name)\s*\=\"(.*?)\"/ ) {
                return ($1,$2);
        } elsif ( $line =~ m/\s*($name)\s*\=(.*)/ ) {
                return ($1,$2);
        } else {
                return ();
        } 
}

# input: Refernece to a hash
# output: Writes modified contents of the hash to the configuration file. The function will preserve comments from the old file.
sub write_config_data { 
        my ( $config_values ) = @_; 
        my $configFileData = read_whole_file($raid_monitor_config); 
        my %keyMap = ();
        
        open( TMP_FILE, ">", TEMP_CONFIG_FILE ) or die "Can't open '" . TEMP_CONFIG_FILE . "' for update: $!";
        
        my %oldKeys = (); 

        #write the values that already existed in the old config file
        for $line (@$configFileData) { 
                chomp($line);
                @keyValue = return_key_value_from_input_line(undef, $line);
                $size = @keyValue;
                if ( $size > 0 ) {
                        $oldKeys->{$keyValue[0]} = $keyValue[1]; 
                        if ( defined($config_values->{$keyValue[0]}) ) {
                            write_config_key_value($keyValue[0], $config_values->{$keyValue[0]}, TMP_FILE);
                        } else {
                            write_config_key_value($keyValue[0],$keyValue[1],TMP_FILE);
                        }
                } else {
                        write_config_line($line, TMP_FILE);
                }
        }  
        
        #write any new values into the config file 
        while ( my ($key, $value) = each(%$config_values) ) {
            write_config_key_value($key, $value, TMP_FILE) if not exists $oldKeys->{$key};
        }        

        close(TMP_FILE);
        system("rm", $raid_monitor_config);
        system("mv", TEMP_CONFIG_FILE, $raid_monitor_config);
}

#outputs a key/value pair to a file handle 
sub write_config_key_value {
        my ($key, $value, $fh) = @_;
        printf($fh "%s=\"%s\"\n", $key, $value); 
}

#outputs a line of text to a file handle
sub write_config_line { 
        my ($line, $fh) = @_;
        print $fh $line;         
        print $fh "\n";
}

#reads a text file into an array of lines. 
sub read_whole_file {
        my ($fn) = @_;
        open(FILE, $raid_monitor_config) or die("Unable to open file");
        @data = <FILE>;
        close(FILE);
        return \@data;
}

set_raid_config_file(RAID_MONITOR_CONF);

1;
