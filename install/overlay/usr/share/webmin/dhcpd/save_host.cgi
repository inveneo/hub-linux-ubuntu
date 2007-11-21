#!/usr/bin/perl
# save_host.cgi
# Update, create or delete a host

require './dhcpd-lib.pl';
require './params-lib.pl';
use Data::Dumper;
&ReadParse();
&lock_file($config{'dhcpd_conf'});
($par, $host, $indent, $npar, $nindent) = get_branch('hst');

# check acls
%access = &get_module_acl();
&error_setup("<blink><font color=red>$text{'eacl_aviol'}</font></blink>");
if ($in{'delete'} || ${'inveneo'}) {
	&error("$text{'eacl_np'} $text{'eacl_pdh'}")
		if !&can('rw', \%access, $host, 1);
	}
elsif ($in{'options'}) {
	&error("$text{'eacl_np'} $text{'eacl_psh'}")
		if !&can('r', \%access, $host);
	}
elsif ($in{'new'}) {
	&error("$text{'eacl_np'} $text{'eacl_pih'}")
		unless &can('c', \%access, $host) && 
				&can('rw', \%access, $par) &&
				(!$npar || &can('rw', \%access, $npar));
	}
else {
	&error("$text{'eacl_np'} $text{'eacl_puh'}")
		unless &can('rw', \%access, $host) &&
			(!$npar || &can('rw', \%access, $npar));
	}

# save
if ($in{'delete'}) {
	# Delete this host
	$whatfailed = $text{'shost_faildel'};
        #print $host, " = host;", $par, " = par";
	&save_directive($par, [ $host ], [ ], 0);
	&drop_dhcpd_acl('hst', \%access, $host->{'values'}->[0]);
	}
elsif ($in{'options'}) {
	# Redirect to client options
	&redirect("edit_options.cgi?sidx=$in{'sidx'}&uidx=$in{'uidx'}&gidx=$in{'gidx'}&idx=$in{'idx'}");
	exit;
	}
else {
	&error_setup($text{'shost_failsave'});

	# Validate and save inputs
	$in{'name'} =~ /^[a-z0-9\.\-]+$/i ||
		&error("'$in{'name'}' $text{'shost_invalidhn'}");
	$host->{'comment'} = $in{'desc'};

	# Check for a hostname clash
	if (($in{'new'} || $in{'name'} ne $host->{'values'}->[0]) &&
	    $access{'uniq_hst'}) {
		foreach $h (&get_hosts()) {
                        &error("$text{'eacl_np'} $text{'eacl_uniq'}")
                                if (lc($h->{'values'}->[0]) eq lc($in{'name'}));
                        }
		}
	$host->{'values'} = [ $in{'name'} ];

	if ($in{'hardware'}) {
		# Convert from Windows / Cisco formats
		$in{'hardware'} =~ s/-/:/g;
		if ($in{'hardware'} =~ /^([0-9a-f]{2})([0-9a-f]{2}).([0-9a-f]{2})([0-9a-f]{2}).([0-9a-f]{2})([0-9a-f]{2}).([0-9a-f]{2})([0-9a-f]{2})$/) {
			$in{'hardware'} = "$1:$2:$3:$4:$5:$6";
			}
		$in{'hardware'} =~ /^([0-9a-f]{1,2}:)*[0-9a-f]{1,2}$/i ||
			&error(&text('shost_invalidhwa',$in{'hardware'},$in{'hardware_type'}) );
		@hard = ( { 'name' => 'hardware',
			    'values' => [ $in{'hardware_type'},
					  $in{'hardware'} ] } );
		}
	&save_directive($host, 'hardware', \@hard);

	if ($in{'fixed-address'}) {
		if ($in{'fixed-address'} !~ /^[\w\s\.\-,]+$/ ||
		    $in{'fixed-address'} =~ /(^|[\s,])[-_]/ ||
		    $in{'fixed-address'} =~ /\.([\s,\.]|$)/ ||
		    $in{'fixed-address'} =~ /(^|[\s,])\d+\.[\d\.]*[a-z_]/i) {
			&error(&text('shost_invalidaddr', $in{'fixed-address'}));	
			}
		@fixedip = split(/[,\s]+/, $in{'fixed-address'});
		@fixed = ( { 'name' => 'fixed-address',
			     'values' => [ join(" , ", @fixedip) ] } );
		}
	&save_directive($host, 'fixed-address', \@fixed);

	&parse_params($host);

	@partypes = ( "", "shared-network", "subnet", "group" );
	if (!$npar || $in{'assign'} > 0 && $npar->{'name'} ne $partypes[$in{'assign'}]) {
		if ($in{'jsquirk'}) {
			&error($text{'shost_invassign'});
			}
		else {
			&redirect("edit_host.cgi?assign=".$in{'assign'}.
				"&idx=".$in{'idx'}."&gidx=".$in{'gidx'}.
				"&uidx=".$in{'uidx'}."&sidx=".$in{'sidx'});
			exit;
			}
		}
	if ($in{'new'}) {
		# save acl for new host
		&save_dhcpd_acl('rw', 'hst', \%access, $in{'name'});
		# Add to the end of the parent structure
		&save_directive($npar, [ ], [ $host ], $nindent);
		}
	elsif ($par eq $npar) {
		# Update host
		&save_directive($par, [ $host ], [ $host ], $indent);
		}
	else {
		# Move this host
		&save_directive($par, [ $host ], [ ], 0);
		&save_directive($npar, [ ], [ $host ], $nindent);
		}
	}
&flush_file_lines();
&unlock_file($config{'dhcpd_conf'});
&webmin_log($in{'delete'} ? 'delete' : $in{'new'} ? 'create' : 'modify',
	    'host', $host->{'values'}->[0], \%in);
if ($in{'ret'} eq "group") {
	$retparms = "sidx=$in{'sidx'}&uidx=$in{'uidx'}&idx=$in{'gidx'}";
	}
elsif ($in{'ret'} eq "subnet") {
	$retparms = "sidx=$in{'sidx'}&idx=$in{'uidx'}";
	}
elsif ($in{'ret'} eq "shared") {
	$retparms = "idx=$in{'sidx'}";
	}

if ( $in{'inveneo_redirect'} ) {
        &redirect( $in{'inveneo_redirect'} . "?" . ($in{'inveneo_message'} ? ("msg=" . $in{'inveneo_message'}) : "") );
} else {
        &redirect($in{'ret'} ? "edit_$in{'ret'}.cgi?$retparms" : "");
}
