#!/usr/bin/perl

local $format;
local $out;

require "../time/time-lib.pl";

&ReadParse();

&error( $text{ 'acl_nosys' } ) if( $access{ 'sysdate' } );
$err = &set_system_time($in{ 'second' }, $in{'minute'}, $in{'hour'},
               $in{'date'}, $in{'month'}-1, $in{'year'}-1900);
&error($err) if ($err);
&webmin_log("set", "date", time(), \%in);

# Set hardware time to system time
&error( $text{ 'acl_nohw' } ) if( $access{ 'hwdate' } && $access{'sysdate'} );
$out = &backquote_logged("hwclock --systohc");
&error( &text( 'error_sync', $out ) ) if( $out ne "" );
&webmin_log("sync_s");

&redirect("");
