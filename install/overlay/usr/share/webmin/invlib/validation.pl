sub is_blank {
   my $val = shift;
   return $val =~ /^\s*$/;
}

sub is_valid_username {
   my $val = shift;
   return !( $val =~ /\W+/ ) && !( $val =~ /^\s*$/ ) && !( $val =~ /^_/ ) && length($val) >= 3;
}

sub generate_error_list {
   my @err_list = @_;
   my $ret_str = "<ul align='right'>";
   foreach (@err_list) {
      $ret_str = $ret_str . "<li>" . $_ . "</li>";
   }
   $ret_str .= "</ul>";
   return $ret_str;
}

1;
