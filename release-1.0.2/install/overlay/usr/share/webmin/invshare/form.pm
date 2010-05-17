
sub input_box_row { 
   $name = shift; 
   $title = shift; 
    
   print "<tr><td valign='top'><b>$title</b></td>\n";
   print "<td valign='top'>",&ui_textbox("$name", undef, 32),"</td></tr>\n";
}

sub print_row_title { 
   $title = shift; 
   $value = shift;
    
   print "<tr><td valign='top'><b>$title</b></td>\n";
   print "<td valign='top'>",$value,"<td></tr>\n";
}

1;
