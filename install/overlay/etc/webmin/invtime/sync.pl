#!/usr/bin/perl
open(CONF, "/etc/webmin/miniserv.conf");
while(<CONF>) {
        $root = $1 if (/^root=(.*)/);
        }
close(CONF);
$ENV{'WEBMIN_CONFIG'} = "/etc/webmin";
$ENV{'WEBMIN_VAR'} = "/var/webmin";
chdir("$root/time");
exec("$root/time/sync.pl", @ARGV) || die "Failed to run $root/time/sync.pl : $!";
