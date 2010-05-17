
sub input_box_row { 
   $name = shift; 
   $title = shift; 
   $value = shift;
    
   print "<tr><td valign='top'><b>$title</b></td>\n";
   print "<td valign='top'>",&ui_textbox("$name", $value, 32),"</td></tr>\n";
}

sub print_row_title { 
   $title = shift; 
   $value = shift;
    
   print "<tr><td valign='top'><b>$title</b></td>\n";
   print "<td valign='top'>",$value,"<td></tr>\n";
}

sub onchange_select() {
   local ( $name, $selected, $options, $onchangeScript ) = @_;  
   local $str;
   $onchangeScript =~ s/\'/\"/g;
   $str = "<select name='$name' id='$name' onchange='$onchangeScript'>";
   foreach $pair ( @{$options} ) {
      $value = @{$pair}[0];
      $label = @{$pair}[1];      
      $selStr = ( $selected eq $value ) ? "SELECTED" : "";
      $str .= "<option value='" . @{$pair}[0] . "' $selStr>" . @{$pair}[1] . "</option>";
   }
   $str .= "</select>";
   return $str;
}

1;
