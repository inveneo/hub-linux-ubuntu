#!/usr/bin/perl

local $format;
local $out;

require "./time-lib.pl";
require 'timelocal.pl';

&ReadParse();

if (!$in{'action'}) {
	# user probably hit return in the time server field
	$in{'action'} = $text{ 'action_timeserver_sys' };
	}
$mode = "time";

if( $in{ 'action' } eq $text{ 'action_apply' } )
{
  # Setting the system time
  &error( $text{ 'acl_nosys' } ) if( $access{ 'sysdate' } );
  $err = &set_system_time($in{ 'second' }, $in{'minute'}, $in{'hour'},
		   $in{'date'}, $in{'month'}-1, $in{'year'}-1900);
  &error($err) if ($err);
  &webmin_log("set", "date", time(), \%in);

=pod
} elsif ( $in{ 'action' } eq $text{ 'action_save' } ) {
  # Setting the hardware time
  &error( $text{ 'acl_nohw' } ) if( $access{ 'hwdate' } );
  $err = &set_hardware_time($in{ 'second' }, $in{'minute'}, $in{'hour'},
		   $in{'date'}, $in{'month'}-1, $in{'year'}-1900);
  &error( &text( 'error_hw', $err ) ) if ($err);
  local $hwtime = timelocal($in{'second'}, $in{'minute'}, $in{'hour'},
			    $in{'date'}, $in{'month'}-1, $in{'year'} < 200 ?
			    $in{'year'} : $in{'year'}-1900);
  &webmin_log("set", "hwclock", $hwtime, \%in);

} elsif( $in{ 'action' } eq $text{ 'action_sync' } ) {
  # Set system time to hardware time
  &error( $text{ 'acl_nosys' } ) if( $access{ 'sysdate' } );
  $out = &backquote_logged("hwclock --hctosys");
  &error( &text( 'error_sync', $out ) ) if( $out ne "" );
  &webmin_log("sync");

} elsif( $in{ 'action' } eq $text{ 'action_sync_s' } ) {
=cut
  # Set hardware time to system time
  &error( $text{ 'acl_nohw' } ) if( $access{ 'hwdate' } && $access{'sysdate'} );
  $out = &backquote_logged("hwclock --systohc");
  &error( &text( 'error_sync', $out ) ) if( $out ne "" );
  &webmin_log("sync_s");

=pod
} elsif( $in{ 'action' } eq $text{ 'index_sync' }) {
  # Sync with a time server
  $access{'ntp'} || &error($text{'acl_nontp'});
  $in{'timeserver'} =~ /\S/ || &error($text{'error_etimeserver'});
  $err = &sync_time($in{'timeserver'}, $in{'hardware'});
  &error($err) if ($err);

  # Save settings in module config
  &lock_file($module_config_file);
  $config{'timeserver'} = $in{'timeserver'};
  $config{'timeserver_hardware'} = $in{'hardware'};
  &save_module_config();
  &unlock_file($module_config_file);

  # Create, update or delete the syncing cron job
  &foreign_require("cron", "cron-lib.pl");
  $oldjob = $job = &find_cron_job();
  $job ||= { 'command' => $cron_cmd,
	     'active' => 1,
	     'user' => 'root' };
  &cron::parse_times_input($job, \%in) if ($in{'sched'});
  &lock_file(&cron::cron_file($job));
  &cron::create_wrapper($cron_cmd, $module_name, "sync.pl");
  if ($in{'sched'} && $oldjob) {
	# Update job
	&cron::change_cron_job($job);
	}
  elsif ($in{'sched'} && !$oldjob) {
	# Create wrapper script and job
	&cron::create_cron_job($job);
	}
  elsif (!$in{'sched'} && $oldjob) {
	# Delete job
	&cron::delete_cron_job($job);
	}
  &unlock_file(&cron::cron_file($job));

  &webmin_log("remote", $in{'action'} eq $text{'action_timeserver_sys'} ?  "date" : "hwclock", $rawtime, \%in);
  $mode = "sync";
=cut
}

&redirect("index.cgi?mode=$mode");

