#!/usr/bin/perl
# Either redirects to link.cgi, if a URL has been set, or asks for a URL
require '../invlib/validation.pl';
require '../invlib/form.pm';
require '../time/freebsd-lib.pl';
require '../time/time-lib.pl';
&ReadParse();

my $hour, $min, $sec;
my $day, $month, $year;
my $msg;

#   ------
sub isLeap
#   ------
{
    my $year = shift;
    return 0 if $year % 4;
    return 1 if $year < 1753;
    return 1 if $year % 100;
    return 1 unless $year % 400;
    return 0;
}

#   -------
sub valDate
#   -------
{
    my ($year, $month, $day) = @_;
    my $daysinm = [
       [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
       [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]];
    return 0 if $year < 1 or $year > 9999;
    return 0 if $month < 1 or $month > 12;
    return 0 if $day < 1 or
       $day > $daysinm->[isLeap($year)]->[$month - 1];
    return 0 if $year == 1752 and $month == 9 and
       ($day > 2 and $day < 14);
    return 1;
}

sub validate_input {
        my @errors = (); 
        if ( valDate($year,$month,$day) eq 0 ) {
            push(@errors, "An invalid date was provided.");
        } 
        return @errors;
}

sub isSelectedValue {
        local ($thisValue, $selectedValues) = @_;
        foreach $value (@{$selectedValues}) {
                return 1 if ( $thisValue == $value );
        }
        return 0;
}

sub generate_select {
        local ($name, $onclick, $children, $selectedValues) = @_;
        local $retVal="";

        if (defined($onclick)) {
            $onclickHtml = "onclick='$onclick'";
        } else {
            $onclickHtml = "";
        }

        $retVal .= "<select name='$name' $onclickHtml>";
        foreach $option (@$children) {
            $label = ${$option}[0];
            $value = ${$option}[1];
            $selected = isSelectedValue($value, $selectedValues) ? "selected" : ""; 
            $retVal .= "<option value='$value' $selected>$label</option>";
        }

        $retVal .= "</select>";
        return $retVal;
}

sub options {
        local ($labels, $values) = @_;
        local $x;
        local $retVal = [];
        local $size = @{$labels};
        for ( $x=0; $x<$size; $x++ ) {
                push(@{$retVal}, [${$labels}[$x],${$values}[$x]]);                
        }
        return $retVal;
}


sub set_defaults {
    if ( defined $in{'form_post'} ) {
        $hour = $in{'hour'};
        $min = $in{'min'};
        $sec = $in{'sec'};        
        $day = $in{'day'};
        $month = $in{'month'};
        $year = $in{'year'};
    } else {
        @syst = get_system_time();
        $hour = $syst[2];
        $min = $syst[1];
        $sec = $syst[0];        
        $day = $syst[3];
        $month = $syst[4]+1;
        $year = $syst[5]-100+2000;
    }
} 

&ui_print_header(undef, $module_info{'desc'}, "", undef, 1, 1);

#print "system time is " . join(':', @syst) . "<br>";
#print "hardware time is " . join(':',get_hardware_time());

# read the form vaules
set_defaults();
if ( defined $in{'form_post'} ) {
        @errors = validate_input();
        if ( @errors > 0 ) {
                for $str (@errors) {
                        print "<p><font color='#ff0000'>- $str</font>";
                }
                print "<br><br>";
        } else {
                #print "date: $month, $day, $year<br>time: $hour, $min, $sec<br>";
                &set_current_timezone($in{'zone'});
                set_system_time($sec, $min, $hour, $day, $month-1, $year);
                $msg = 'The date/time information was updated.';
        }
} 

if ( defined $msg ) {
    print "<p>$msg</p><br><br>";
}

print "<h2>Time Management</h2>";

print &ui_form_start("index.cgi");
print "<input type='hidden' name='form_post' value='1'></input>";
print "<table cellpadding='5'>";
$monthHtml = generate_select('month',"",options([1..12],[1..12]),[$month]);
$dayHtml = generate_select('day',"",options([1..31],[1..31]),[$day]);
$yearHtml = generate_select('year',"",options([1965..2099],[1965..2099]),[$year]);
print <<HTML;
<tr>
        <td><b>Date</b></td>
</tr>
<tr>
        <td>Month:</td><td>$monthHtml</td>
        <td>Day:</td><td>$dayHtml</td>
        <td>Year:</td><td>$yearHtml</td>
</tr>
HTML

$hourHtml = generate_select('hour',"",options([0..23],[0..23]),[$hour]);
$minHtml = generate_select('min',"",options([0..59],[0..59]),[$min]);
$secHtml = generate_select('sec',"",options([0..59],[0..59]),[$sec]);
print <<HTML;
<tr>
        <td><b>Time</b></td>
</tr>
<tr>
        <td>Hour:</td><td>$hourHtml</td>
        <td>Min:</td><td>$minHtml</td>
        <td>Second:</td><td>$secHtml</td>
</tr>
HTML

@zones = &list_timezones();
$cz = &get_current_timezone();
$found = 0;

print "</table>";
print "<table>";
print "<tr> <td><b>Timezone:</b></td></tr>\n";
print "<tr><td colspan='6'><select name=zone>\n";
foreach $z (@zones) {
        if ($z->[0] =~ /^(.*)\/(.*)$/) {
                $pfx = $1;
        } else {
                $pfx = undef;
        }
        if ($pfx ne $lastpfx && $z ne $zones[0]) {
                print "<option value=''>----------\n";
        }
        $lastpfx = $pfx;
        printf "<option value=%s %s>%s\n",
                $z->[0], $cz eq $z->[0] ? "selected" : "",
                $z->[1] ? "$z->[0] ($z->[1])" : $z->[0];
        $found = 1 if ($cz eq $z->[0]);
}
if (!$found && $cz) {
        printf "<option value=%s %s>%s\n",
                $cz, "selected", $cz;
}
print "</select></td> </tr>\n";
print "<tr><td colspan='7'><input type='submit' value='Save'></input></td></tr>";
print "</table>";

print &ui_form_end();

&ui_print_footer("/", $text{'index'});
