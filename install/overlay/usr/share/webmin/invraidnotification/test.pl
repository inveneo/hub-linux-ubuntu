use raidalertconfig; 

use Test::Simple tests => 16; 

# test reading config items from the file
set_raid_config_file('testdata/raid_monitor.conf');
%expectedValues= (
        'MONITOR_SMTP_USERNAME' => 'testing1',
        'MONITOR_SMTP_HOSTNAME' => 'testing2',
        'MONITOR_SMTP_PORT' => 'testing3'
);

$configValues = read_config_items( keys(%expectedValues) );

while ( my ($key, $actualValue) = each(%$configValues) ) {
        $expectedValue = $expectedValues{$key};
        print "key: $key\nexpected: $expectedValue\nactual: $actualValue\n";
        ok( $expectedValue eq $actualValue );
}

# test writing to config files
$configValues->{'MONITOR_SMTP_USERNAME'} = "1";
$configValues->{'MONITOR_SMTP_HOSTNAME'} = "2";
$configValues->{'MONITOR_SMTP_PORT'} = "3";
write_config_data($configValues);
%expectedValues= (
        'MONITOR_SMTP_USERNAME' => '1',
        'MONITOR_SMTP_HOSTNAME' => '2',
        'MONITOR_SMTP_PORT' => '3', 
        'MONITOR_EXPECTED_NUM_DRIVES' => '1', 
        'EMAIL_INTERVAL' => '1440', 
        'BEEP_INTERVAL' => '60',
        'MONITOR_SMTP_PASSWORD' => '1qaz2wsx',
        'MONITOR_SMTP_TLS' => '1',
        'MONITOR_SMTP_SENDER' => 'inveneo.smtp@gmail.com',
        'MONITOR_SMTP_DEFAULT_MESSAGE' => 'Host has a failed disk drive:',
        'MONITOR_SMTP_DEFAULT_SUBJECT' => 'Subject: CRITICAL PROBLEM: A hard disk has failed',
        'MONITOR_SMTP_RECIPIENT' => '',
        'BEEP_CMD' => 'beep -f 1000 -n -f 1200 -n -f 1500 -n -f 1700 -n -f 1950 -n -f 2200 -n -f 2400 -n -f 2700' 
        );

$configValues = read_config_items( keys(%expectedValues) );
while ( my ($key, $actualValue) = each(%$configValues) ) {
        $expectedValue = $expectedValues{$key};
        print "key: $key\nexpected: $expectedValue\nactual: $actualValue\n";
        ok( $expectedValue eq $actualValue );
}

$configValues->{'MONITOR_SMTP_USERNAME'} = "testing1";
$configValues->{'MONITOR_SMTP_HOSTNAME'} = "testing2";
$configValues->{'MONITOR_SMTP_PORT'} = "testing3";
write_config_data($configValues);

