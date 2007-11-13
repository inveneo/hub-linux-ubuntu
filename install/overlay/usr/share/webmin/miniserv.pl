#!/usr/bin/perl
# A very simple perl web server used by Webmin

# Require basic libraries
package miniserv;
use Socket;
use POSIX;

# Find and read config file
if (@ARGV != 1) {
	die "Usage: miniserv.pl <config file>";
	}
if ($ARGV[0] =~ /^([a-z]:)?\//i) {
	$config_file = $ARGV[0];
	}
else {
	chop($pwd = `pwd`);
	$config_file = "$pwd/$ARGV[0]";
	}
%config = &read_config_file($config_file);

# Check is SSL is enabled and available
if ($config{'ssl'}) {
	eval "use Net::SSLeay";
	if (!$@) {
		$use_ssl = 1;
		# These functions only exist for SSLeay 1.0
		eval "Net::SSLeay::SSLeay_add_ssl_algorithms()";
		eval "Net::SSLeay::load_error_strings()";
		if ($config{'no_ssl2'}) {
			eval "Net::SSLeay::CTX_set_options($ctx,&Net::SSLeay::OP_NO_SSLv2)";
			}
		if (defined(&Net::SSLeay::X509_STORE_CTX_get_current_cert) &&
		    defined(&Net::SSLeay::CTX_load_verify_locations) &&
		    defined(&Net::SSLeay::CTX_set_verify)) {
			$client_certs = 1;
			}
		}
	}

# Check if the syslog module is available to log hacking attempts
if ($config{'syslog'} && !$config{'inetd'}) {
	eval "use Sys::Syslog qw(:DEFAULT setlogsock)";
	if (!$@) {
		$use_syslog = 1;
		}
	}

# check if the TCP-wrappers module is available
if ($config{'libwrap'}) {
	eval "use Authen::Libwrap qw(hosts_ctl STRING_UNKNOWN)";
	if (!$@) {
		$use_libwrap = 1;
		}
	}

# Get miniserv's perl path and location
$miniserv_path = $0;
open(SOURCE, $miniserv_path);
<SOURCE> =~ /^#!(\S+)/;
$perl_path = $1;
close(SOURCE);
if (!-x $perl_path) {
	$perl_path = $^X;
	}
if (-l $perl_path) {
	$linked_perl_path = readlink($perl_path);
	}
@miniserv_argv = @ARGV;

# Check vital config options
&update_vital_config();

$sidname = $config{'sidname'};
die "Session authentication cannot be used in inetd mode"
	if ($config{'inetd'} && $config{'session'});

# check if the PAM module is available to authenticate
if (!$config{'no_pam'}) {
	eval "use Authen::PAM;";
	if (!$@) {
		# check if the PAM authentication can be used by opening a
		# PAM handle
		local $pamh;
		if (ref($pamh = new Authen::PAM($config{'pam'}, "root",
						  \&pam_conv_func))) {
			# Now test a login to see if /etc/pam.d/XXX is set
			# up properly.
			$pam_conv_func_called = 0;
			$pam_username = "test";
			$pam_password = "test";
			$pamh->pam_authenticate();
			if ($pam_conv_func_called) {
				$pam_msg = "PAM authentication enabled";
				$use_pam = 1;
				}
			else {
				$pam_msg = "PAM test failed - maybe /etc/pam.d/$config{'pam'} does not exist";
				}
			}
		else {
			$pam_msg = "PAM initialization of Authen::PAM failed";
			}
		}
	else {
		$pam_msg = "Perl module Authen::PAM needed for PAM is not installed : $@";
		}
	}
if ($config{'pam_only'} && !$use_pam) {
	$pam_msg2 = "PAM use is mandatory, but could not be enabled!";
	}

# Check if the User::Utmp perl module is installed
if ($config{'utmp'}) {
	eval "use User::Utmp;";
	if (!$@) {
		$write_utmp = 1;
		$utmp_msg = "UTMP logging enabled";
		}
	else {
		$utmp_msg = "Perl module User::Utmp needed for Utmp logging is not installed : $@";
		}
	}

# See if the crypt function fails
eval "crypt('foo', 'xx')";
if ($@) {
	eval "use Crypt::UnixCrypt";
	if (!$@) {
		$use_perl_crypt = 1;
		$crypt_msg = "Using Crypt::UnixCrypt for password encryption\n";
		}
	else {
		$crypt_msg = "crypt() function un-implemented, and Crypt::UnixCrypt not installed - password authentication will probably fail\n";
		}
	}

# Check if /dev/urandom really generates random IDs, by calling it twice
local $rand1 = &generate_random_id("foo", 1);
local $rand2 = &generate_random_id("foo", 2);
local $rand_msg;
if ($rand1 eq $rand2) {
	$bad_urandom = 1;
	$rand_msg = "Random number generator file /dev/urandom is not reliable";
	}

# Check if we can call sudo
if ($config{'sudo'} && &has_command("sudo")) {
	eval "use IO::Pty";
	if (!$@) {
		$use_sudo = 1;
		}
	else {
		$sudo_msg = "Perl module IO::Pty needed for calling sudo is not installed : $@";
		}
	}

# init days and months for http_date
@weekday = ( "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat" );
@month = ( "Jan", "Feb", "Mar", "Apr", "May", "Jun",
	   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" );

# Change dir to the server root
@roots = ( $config{'root'} );
for($i=0; defined($config{"extraroot_$i"}); $i++) {
	push(@roots, $config{"extraroot_$i"});
	}
chdir($roots[0]);
eval { $user_homedir = (getpwuid($<))[7]; };
if ($@) {
	# getpwuid doesn't work on windows
	$user_homedir = $ENV{"HOME"} || $ENV{"USERPROFILE"} || "/";
	$on_windows = 1;
	}

# Read users file
&read_users_file();

# Setup SSL if possible and if requested
if (!-r $config{'keyfile'} ||
    $config{'certfile'} && !-r $config{'certfile'}) {
	# Key file doesn't exist!
	$use_ssl = 0;
	}
@ipkeys = &get_ipkeys(\%config);
if ($use_ssl) {
	if ($config{'ssl_version'}) {
		# Force an SSL version
		$Net::SSLeay::version = $config{'ssl_version'};
		$Net::SSLeay::ssl_version = $config{'ssl_version'};
		}
	$client_certs = 0 if (!-r $config{'ca'} || !%certs);
	$ssl_contexts{"*"} = &create_ssl_context($config{'keyfile'},
						 $config{'certfile'});
	foreach $ipkey (@ipkeys) {
		$ctx = &create_ssl_context($ipkey->{'key'}, $ipkey->{'cert'});
		foreach $ip (@{$ipkey->{'ips'}}) {
			$ssl_contexts{$ip} = $ctx;
			}
		}
	}

# Setup syslog support if possible and if requested
if ($use_syslog) {
	open(ERRDUP, ">&STDERR");
	open(STDERR, ">/dev/null");
	$log_socket = $config{"logsock"} || "unix";
	eval 'openlog($config{"pam"}, "cons,pid,ndelay", "authpriv"); setlogsock($log_socket)';
	if ($@) {
		$use_syslog = 0;
		}
	else {
		local $msg = ucfirst($config{'pam'})." starting";
		eval { syslog("info", "%s", $msg); };
		if ($@) {
			eval {
				setlogsock("inet");
				syslog("info", "%s", $msg);
				};
			if ($@) {
				# All attempts to use syslog have failed..
				$use_syslog = 0;
				}
			}
		}
	open(STDERR, ">&ERRDUP");
	close(ERRDUP);
	}

# Read MIME types file and add extra types
&read_mime_types();

# get the time zone
if ($config{'log'}) {
	local(@gmt, @lct, $days, $hours, $mins);
	@gmt = gmtime(time());
	@lct = localtime(time());
	$days = $lct[3] - $gmt[3];
	$hours = ($days < -1 ? 24 : 1 < $days ? -24 : $days * 24) +
		 $lct[2] - $gmt[2];
	$mins = $hours * 60 + $lct[1] - $gmt[1];
	$timezone = ($mins < 0 ? "-" : "+"); $mins = abs($mins);
	$timezone .= sprintf "%2.2d%2.2d", $mins/60, $mins%60;
	}

# Build various maps from the config files
&build_config_mappings();

# start up external authentication program, if needed
if ($config{'extauth'}) {
	socketpair(EXTAUTH, EXTAUTH2, AF_UNIX, SOCK_STREAM, PF_UNSPEC);
	if (!($extauth = fork())) {
		close(EXTAUTH);
		close(STDIN);
		close(STDOUT);
		open(STDIN, "<&EXTAUTH2");
		open(STDOUT, ">&EXTAUTH2");
		exec($config{'extauth'}) or die "exec failed : $!\n";
		}
	close(EXTAUTH2);
	local $os = select(EXTAUTH);
	$| = 1; select($os);
	}

# Pre-load any libraries
foreach $pl (split(/\s+/, $config{'preload'})) {
	($pkg, $lib) = split(/=/, $pl);
	$pkg =~ s/[^A-Za-z0-9]/_/g;
	eval "package $pkg; do '$config{'root'}/$lib'";
	if ($@) {
		print STDERR "Failed to pre-load $pkg/$lib : $@\n";
		}
	else {
		print STDERR "Pre-loading $pkg/$lib\n";
		}
	}

# Open debug log if set
if ($config{'debuglog'}) {
	open(DEBUG, ">>$config{'debuglog'}");
	chmod(0700, $config{'debuglog'});
	select(DEBUG); $| = 1; select(STDOUT);
	print DEBUG "miniserv.pl starting ..\n";
	}

# Write out (empty) blocked hosts file
&write_blocked_file();

# Re-direct STDERR to a log file
if ($config{'errorlog'} ne '-') {
	open(STDERR, ">>$config{'errorlog'}") || die "failed to open $config{'errorlog'} : $!";
	if ($config{'logperms'}) {
		chmod(oct($config{'logperms'}), $config{'errorlog'});
		}
	}
select(STDERR); $| = 1; select(STDOUT);

if ($config{'inetd'}) {
	# We are being run from inetd - go direct to handling the request
	$SIG{'HUP'} = 'IGNORE';
	$SIG{'TERM'} = 'DEFAULT';
	$SIG{'PIPE'} = 'DEFAULT';
	open(SOCK, "+>&STDIN");

	# Check if it is time for the logfile to be cleared
	if ($config{'logclear'}) {
		local $write_logtime = 0;
		local @st = stat("$config{'logfile'}.time");
		if (@st) {
			if ($st[9]+$config{'logtime'}*60*60 < time()){
				# need to clear log
				$write_logtime = 1;
				unlink($config{'logfile'});
				}
			}
		else { $write_logtime = 1; }
		if ($write_logtime) {
			open(LOGTIME, ">$config{'logfile'}.time");
			print LOGTIME time(),"\n";
			close(LOGTIME);
			}
		}

	# Initialize SSL for this connection
	if ($use_ssl) {
		$ssl_con = &ssl_connection_for_ip(SOCK);
		$ssl_con || exit;
		}

	# Work out the hostname for this web server
	$host = &get_socket_name(SOCK);
	$host || exit;
	$port = $config{'port'};
	$acptaddr = getpeername(SOCK);
	$acptaddr || exit;

	print DEBUG "main: Starting handle_request loop pid=$$\n";
	while(&handle_request($acptaddr, getsockname(SOCK))) { }
	print DEBUG "main: Done handle_request loop pid=$$\n";
	close(SOCK);
	exit;
	}

# Build list of sockets to listen on
if ($config{"bind"} && $config{"bind"} ne "*") {
	push(@sockets, [ inet_aton($config{'bind'}), $config{'port'} ]);
	}
else {
	push(@sockets, [ INADDR_ANY, $config{'port'} ]);
	}
foreach $s (split(/\s+/, $config{'sockets'})) {
	if ($s =~ /^(\d+)$/) {
		# Just listen on another port on the main IP
		push(@sockets, [ $sockets[0]->[0], $s ]);
		}
	elsif ($s =~ /^(\S+):(\d+)$/) {
		# Listen on a specific port and IP
		push(@sockets, [ $1 eq "*" ? INADDR_ANY : inet_aton($1), $2 ]);
		}
	elsif ($s =~ /^([0-9\.]+):\*$/ || $s =~ /^([0-9\.]+)$/) {
		# Listen on the main port on another IP
		push(@sockets, [ inet_aton($1), $sockets[0]->[1] ]);
		}
	}

# Open all the sockets
$proto = getprotobyname('tcp');
@sockerrs = ( );
$tried_inaddr_any = 0;
for($i=0; $i<@sockets; $i++) {
	$fh = "MAIN$i";
	socket($fh, PF_INET, SOCK_STREAM, $proto) ||
		die "Failed to open socket : $!";
	setsockopt($fh, SOL_SOCKET, SO_REUSEADDR, pack("l", 1));
	for($j=0; $j<5; $j++) {
		last if (bind($fh, pack_sockaddr_in($sockets[$i]->[1],
						    $sockets[$i]->[0])));
		sleep(1);
		}
	if ($j == 5) {
		# All attempts failed .. give up
		if ($sockets[$i]->[0] eq INADDR_ANY) {
			push(@sockerrs, "Failed to bind to port $sockets[$i]->[1] : $!");
			$tried_inaddr_any = 1;
			}
		else {
			$ip = inet_ntoa($sockets[$i]->[0]);
			push(@sockerrs, "Failed to bind to IP $ip port $sockets[$i]->[1] : $!");
			}
		}
	else {
		listen($fh, SOMAXCONN);
		push(@socketfhs, $fh);
		}
	}
foreach $se (@sockerrs) {
	print STDERR $se,"\n";
	}

# If all binds failed, try binding to any address
if (!@socketfhs && !$tried_inaddr_any) {
	print STDERR "Falling back to listening on any address\n";
	$fh = "MAIN";
	socket($fh, PF_INET, SOCK_STREAM, $proto) ||
		die "Failed to open socket : $!";
	setsockopt($fh, SOL_SOCKET, SO_REUSEADDR, pack("l", 1));
	bind($fh, pack_sockaddr_in($sockets[0]->[1], INADDR_ANY)) ||
		die "Failed to bind to port $sockets[0]->[1] : $!";
	listen($fh, SOMAXCONN);
	push(@socketfhs, $fh);
	}

if ($config{'listen'}) {
	# Open the socket that allows other webmin servers to find this one
	$proto = getprotobyname('udp');
	if (socket(LISTEN, PF_INET, SOCK_DGRAM, $proto)) {
		setsockopt(LISTEN, SOL_SOCKET, SO_REUSEADDR, pack("l", 1));
		bind(LISTEN, pack_sockaddr_in($config{'listen'}, INADDR_ANY));
		listen(LISTEN, SOMAXCONN);
		}
	else {
		$config{'listen'} = 0;
		}
	}

# Split from the controlling terminal, unless configured not to
if (!$config{'nofork'}) {
	if (fork()) { exit; }
	}
eval { setsid(); };	# may not work on Windows

# Close standard file handles
open(STDIN, "</dev/null");
open(STDOUT, ">/dev/null");
&log_error("miniserv.pl started");
&log_error($pam_msg) if ($pam_msg);
&log_error($pam_msg2) if ($pam_msg2);
&log_error($utmp_msg) if ($utmp_msg);
&log_error($crypt_msg) if ($crypt_msg);
&log_error($sudo_msg) if ($sudo_msg);
&log_error($rand_msg) if ($rand_msg);

# write out the PID file
open(PIDFILE, ">$config{'pidfile'}");
printf PIDFILE "%d\n", getpid();
close(PIDFILE);

# Start the log-clearing process, if needed. This checks every minute
# to see if the log has passed its reset time, and if so clears it
if ($config{'logclear'}) {
	if (!($logclearer = fork())) {
		&close_all_sockets();
		close(LISTEN);
		while(1) {
			local $write_logtime = 0;
			local @st = stat("$config{'logfile'}.time");
			if (@st) {
				if ($st[9]+$config{'logtime'}*60*60 < time()){
					# need to clear log
					$write_logtime = 1;
					unlink($config{'logfile'});
					}
				}
			else { $write_logtime = 1; }
			if ($write_logtime) {
				open(LOGTIME, ">$config{'logfile'}.time");
				print LOGTIME time(),"\n";
				close(LOGTIME);
				}
			sleep(5*60);
			}
		exit;
		}
	push(@childpids, $logclearer);
	}

# Setup the logout time dbm if needed
if ($config{'session'}) {
	eval "use SDBM_File";
	dbmopen(%sessiondb, $config{'sessiondb'}, 0700);
	eval "\$sessiondb{'1111111111'} = 'foo bar';";
	if ($@) {
		dbmclose(%sessiondb);
		eval "use NDBM_File";
		dbmopen(%sessiondb, $config{'sessiondb'}, 0700);
		}
	else {
		delete($sessiondb{'1111111111'});
		}
	}

# Run the main loop
$SIG{'HUP'} = 'miniserv::trigger_restart';
$SIG{'TERM'} = 'miniserv::term_handler';
$SIG{'USR1'} = 'miniserv::trigger_reload';
$SIG{'PIPE'} = 'IGNORE';
local $remove_session_count = 0;
$need_pipes = $config{'passdelay'} || $config{'session'};
while(1) {
	# wait for a new connection, or a message from a child process
	local ($i, $rmask);
	if (@childpids <= $config{'maxconns'}) {
		# Only accept new main socket connects when ready
		local $s;
		foreach $s (@socketfhs) {
			vec($rmask, fileno($s), 1) = 1;
			}
		}
	else {
		printf STDERR "too many children (%d > %d)\n",
			scalar(@childpids), $config{'maxconns'};
		}
	if ($need_pipes) {
		for($i=0; $i<@passin; $i++) {
			vec($rmask, fileno($passin[$i]), 1) = 1;
			}
		}
	vec($rmask, fileno(LISTEN), 1) = 1 if ($config{'listen'});

	# Wait for a connection
	local $sel = select($rmask, undef, undef, 10);

	# Check the flag files
	if ($config{'restartflag'} && -r $config{'restartflag'}) {
		print STDERR "restart flag file detected\n";
		unlink($config{'restartflag'});
		$need_restart = 1;
		}
	if ($config{'reloadflag'} && -r $config{'reloadflag'}) {
		unlink($config{'reloadflag'});
		$need_reload = 1;
		}

	if ($need_restart) {
		# Got a HUP signal while in select() .. restart now
		&restart_miniserv();
		}
	if ($need_reload) {
		# Got a USR1 signal while in select() .. re-read config
		$need_reload = 0;
		&reload_config_file();
		}
	local $time_now = time();

	# Clean up finished processes
	local $pid;
	do {	$pid = waitpid(-1, WNOHANG);
		@childpids = grep { $_ != $pid } @childpids;
		} while($pid != 0 && $pid != -1);

	# run the unblocking procedure to check if enough time has passed to
	# unblock hosts that heve been blocked because of password failures
	$unblocked = 0;
	if ($config{'blockhost_failures'}) {
		$i = 0;
		while ($i <= $#deny) {
			if ($blockhosttime{$deny[$i]} &&
			    $config{'blockhost_time'} != 0 &&
			    ($time_now - $blockhosttime{$deny[$i]}) >=
			     $config{'blockhost_time'}) {
				# the host can be unblocked now
				$hostfail{$deny[$i]} = 0;
				splice(@deny, $i, 1);
				$unblocked = 1;
				}
			$i++;
			}
		}

	# Do the same for blocked users
	if ($config{'blockuser_failures'}) {
		$i = 0;
		while ($i <= $#deny) {
			if ($blockusertime{$deny[$i]} &&
			    $config{'blockuser_time'} != 0 &&
			    ($time_now - $blockusertime{$deny[$i]}) >=
			     $config{'blockuser_time'}) {
				# the user can be unblocked now
				$userfail{$deny[$i]} = 0;
				splice(@denyusers, $i, 1);
				$unblocked = 1;
				}
			$i++;
			}
		}
	if ($unblocked) {
		&write_blocked_file();
		}

	if ($config{'session'} && (++$remove_session_count%50) == 0) {
		# Remove sessions with more than 7 days of inactivity,
		local $s;
		foreach $s (keys %sessiondb) {
			local ($user, $ltime, $lip) = split(/\s+/, $sessiondb{$s});
			if ($time_now - $ltime > 7*24*60*60) {
				&run_logout_script($s, $user);
				&write_logout_utmp($user, $lip);
				delete($sessiondb{$s});
				if ($use_syslog) {
					syslog("info", "%s",
					      "Timeout of session for $user");
					}
				}
			}
		}

	if ($use_pam && $config{'pam_conv'}) {
		# Remove PAM sessions with more than 5 minutes of inactivity
		local $c;
		foreach $c (values %conversations) {
			if ($time_now - $c->{'time'} > 5*60) {
				&end_pam_conversation($c);
				if ($use_syslog) {
					syslog("info", "%s", "Timeout of PAM ".
						"session for $c->{'user'}");
					}
				}
			}
		}

	# Don't check any sockets if there is no activity
	next if ($sel <= 0);

	# Check if any of the main sockets have received a new connection
	local $sn = 0;
	foreach $s (@socketfhs) {
		if (vec($rmask, fileno($s), 1)) {
			# got new connection
			$acptaddr = accept(SOCK, $s);
			if (!$acptaddr) { next; }
			binmode(SOCK);	# turn off any Perl IO stuff

			# create pipes
			local ($PASSINr, $PASSINw, $PASSOUTr, $PASSOUTw);
			if ($need_pipes) {
				($PASSINr, $PASSINw, $PASSOUTr, $PASSOUTw) =
					&allocate_pipes();
				}

			# Check username of connecting user
			local ($peerp, $peera) = unpack_sockaddr_in($acptaddr);
			$localauth_user = undef;
			if ($config{'localauth'} && inet_ntoa($peera) eq "127.0.0.1") {
				if (open(TCP, "/proc/net/tcp")) {
					# Get the info direct from the kernel
					while(<TCP>) {
						s/^\s+//;
						local @t = split(/[\s:]+/, $_);
						if ($t[1] eq '0100007F' &&
						    $t[2] eq sprintf("%4.4X", $peerp)) {
							$localauth_user = getpwuid($t[11]);
							last;
							}
						}
					close(TCP);
					}
				else {
					# Call lsof for the info
					local $lsofpid = open(LSOF,
						"$config{'localauth'} -i TCP\@127.0.0.1:$peerp |");
					while(<LSOF>) {
						if (/^(\S+)\s+(\d+)\s+(\S+)/ &&
						    $2 != $$ && $2 != $lsofpid) {
							$localauth_user = $3;
							}
						}
					close(LSOF);
					}
				}

			# Work out the hostname for this web server
			$host = &get_socket_name(SOCK);
			if (!$host) {
				print STDERR "Failed to get local socket name : $!\n";
				close(SOCK);
				next;
				}
			$port = $sockets[$sn]->[1];

			# fork the subprocess
			local $handpid;
			if (!($handpid = fork())) {
				# setup signal handlers
				$SIG{'TERM'} = 'DEFAULT';
				$SIG{'PIPE'} = 'DEFAULT';
				#$SIG{'CHLD'} = 'IGNORE';
				$SIG{'HUP'} = 'IGNORE';
				$SIG{'USR1'} = 'IGNORE';

				# Initialize SSL for this connection
				if ($use_ssl) {
					$ssl_con = &ssl_connection_for_ip(SOCK);
					$ssl_con || exit;
					}

				# Close the file handle for the session DBM
				dbmclose(%sessiondb);

				# close useless pipes
				if ($need_pipes) {
					&close_all_pipes();
					close($PASSINr); close($PASSOUTw);
					}
				&close_all_sockets();
				close(LISTEN);

				print DEBUG
				  "main: Starting handle_request loop pid=$$\n";
				while(&handle_request($acptaddr,
						      getsockname(SOCK))) { }
				print DEBUG
				  "main: Done handle_request loop pid=$$\n";
				shutdown(SOCK, 1);
				close(SOCK);
				close($PASSINw); close($PASSOUTw);
				exit;
				}
			push(@childpids, $handpid);
			if ($need_pipes) {
				close($PASSINw); close($PASSOUTr);
				push(@passin, $PASSINr);
				push(@passout, $PASSOUTw);
				}
			close(SOCK);
			}
		$sn++;
		}

	if ($config{'listen'} && vec($rmask, fileno(LISTEN), 1)) {
		# Got UDP packet from another webmin server
		local $rcvbuf;
		local $from = recv(LISTEN, $rcvbuf, 1024, 0);
		next if (!$from);
		local $fromip = inet_ntoa((unpack_sockaddr_in($from))[1]);
		local $toip = inet_ntoa((unpack_sockaddr_in(
					 getsockname(LISTEN)))[1]);
		if ((!@deny || !&ip_match($fromip, $toip, @deny)) &&
		    (!@allow || &ip_match($fromip, $toip, @allow))) {
			local $listenhost = &get_socket_name(LISTEN);
			send(LISTEN, "$listenhost:$config{'port'}:".
				  ($use_ssl || $config{'inetd_ssl'} ? 1 : 0).":".
				  ($config{'listenhost'} ?
					&get_system_hostname() : ""),
				  0, $from)
				if ($listenhost);
			}
		}

	# check for session, password-timeout and PAM messages from subprocesses
	for($i=0; $i<@passin; $i++) {
		if (vec($rmask, fileno($passin[$i]), 1)) {
			# this sub-process is asking about a password
			local $infd = $passin[$i];
			local $outfd = $passout[$i];
			#local $inline = <$infd>;
			local $inline = &sysread_line($infd);
			if ($inline) {
				print DEBUG "main: inline $inline";
				}
			else {
				print DEBUG "main: inline EOF\n";
				}
			if ($inline =~ /^delay\s+(\S+)\s+(\S+)\s+(\d+)/) {
				# Got a delay request from a subprocess.. for
				# valid logins, there is no delay (to prevent
				# denial of service attacks), but for invalid
				# logins the delay increases with each failed
				# attempt.
				if ($3) {
					# login OK.. no delay
					print $outfd "0 0\n";
					$wasblocked = $hostfail{$2} ||
						      $userfail{$1};
					$hostfail{$2} = 0;
					$userfail{$1} = 0;
					if ($wasblocked) {
						&write_blocked_file();
						}
					}
				else {
					# login failed..
					$hostfail{$2}++;
					$userfail{$1}++;
					$blocked = 0;

					# add the host to the block list,
					# if configured
 					if ($config{'blockhost_failures'} &&
					    $hostfail{$2} >=
					      $config{'blockhost_failures'}) {
						push(@deny, $2);
						$blockhosttime{$2} = $time_now;
						$blocked = 1;
						if ($use_syslog) {
							local $logtext = "Security alert: Host $2 blocked after $config{'blockhost_failures'} failed logins for user $1";
							syslog("crit", "%s",
								$logtext);
							}
						}

					# add the user to the user block list,
					# if configured
 					if ($config{'blockuser_failures'} &&
					    $userfail{$1} >=
					      $config{'blockuser_failures'}) {
						push(@denyusers, $1);
						$blockusertime{$1} = $time_now;
						$blocked = 2;
						if ($use_syslog) {
							local $logtext = "Security alert: User $1 blocked after $config{'blockuser_failures'} failed logins";
							syslog("crit", "%s",
								$logtext);
							}
						}

					# Send back a delay
					$dl = $userdlay{$1} -
				           int(($time_now - $userlast{$1})/50);
					$dl = $dl < 0 ? 0 : $dl+1;
					print $outfd "$dl $blocked\n";
					$userdlay{$1} = $dl;

					# Write out blocked status file
					if ($blocked) {
						&write_blocked_file();
						}
					}
				$userlast{$1} = $time_now;
				}
			elsif ($inline =~ /^verify\s+(\S+)\s+(\S+)/) {
				# Verifying a session ID
				local $session_id = $1;
				local $notimeout = $2;
				if (!defined($sessiondb{$session_id})) {
					# Session doesn't exist
					print $outfd "0 0\n";
					}
				else {
					local ($user, $ltime) =
					  split(/\s+/, $sessiondb{$session_id});
					local $lot = &get_logout_time($user, $session_id);
					if ($lot &&
					    $time_now - $ltime > $lot*60 &&
					    !$notimeout) {
						# Session has timed out
						print $outfd "1 ",$time_now - $ltime,"\n";
						#delete($sessiondb{$session_id});
						}
					else {
						# Session is OK
						print $outfd "2 $user\n";
						if ($lot &&
						    $time_now - $ltime >
						    ($lot*60)/2) {
							$sessiondb{$session_id} = "$user $time_now";
							}
						}
					}
				}
			elsif ($inline =~ /^new\s+(\S+)\s+(\S+)\s+(\S+)/) {
				# Creating a new session
				$sessiondb{$1} = "$2 $time_now $3";
				}
			elsif ($inline =~ /^delete\s+(\S+)/) {
				# Logging out a session
				local $sid = $1;
				local @sdb = split(/\s+/, $sessiondb{$sid});
				print $outfd $sdb[0],"\n";
				delete($sessiondb{$sid});
				}
			elsif ($inline =~ /^pamstart\s+(\S+)\s+(\S+)\s+(.*)/) {
				# Starting a new PAM conversation
				local ($cid, $host, $user) = ($1, $2, $3);

				# Does this user even need PAM?
				local ($realuser, $canlogin) =
					&can_user_login($user, undef, $host);
				local $conv;
				if ($canlogin == 0) {
					# Cannot even login!
					print $outfd "0 Invalid username\n";
					}
				elsif ($canlogin != 2) {
					# Not using PAM .. so just ask for
					# the password.
					$conv = { 'user' => $realuser,
						  'host' => $host,
						  'step' => 0,
						  'cid' => $cid,
						  'time' => time() };
					print $outfd "3 Password\n";
					}
				else {
					# Start the PAM conversation
					# sub-process, and get a question
					$conv = { 'user' => $realuser,
						  'host' => $host,
						  'cid' => $cid,
						  'time' => time() };
					local ($PAMINr, $PAMINw, $PAMOUTr,
						$PAMOUTw) = &allocate_pipes();
					local $pampid = fork();
					if (!$pampid) {
						close($PAMOUTr); close($PAMINw);
						&pam_conversation_process(
							$realuser,
							$PAMOUTw, $PAMINr);
						}
					close($PAMOUTw); close($PAMINr);
					$conv->{'pid'} = $pampid;
					$conv->{'PAMOUTr'} = $PAMOUTr;
					$conv->{'PAMINw'} = $PAMINw;
					push(@childpids, $pampid);

					# Get the first PAM question
					local $pok = &recv_pam_question(
						$conv, $outfd);
					if (!$pok) {
						&end_pam_conversation($conv);
						}
					}

				$conversations{$cid} = $conv if ($conv);
				}
			elsif ($inline =~ /^pamanswer\s+(\S+)\s+(.*)/) {
				# A response to a PAM question
				local ($cid, $answer) = ($1, $2);
				local $conv = $conversations{$cid};
				if (!$conv) {
					# No such conversation?
					print $outfd "0 Bad login session\n";
					}
				elsif ($conv->{'pid'}) {
					# Send the PAM response and get
					# the next question
					&send_pam_answer($conv, $answer);
					local $pok = &recv_pam_question($conv, $outfd);
					if (!$pok) {
						&end_pam_conversation($conv);
						}
					}
				else {
					# This must be the password .. try it
					# and send back the results
					local ($vu, $expired, $nonexist) =
						&validate_user($conv->{'user'},
							       $answer,
							       $conf->{'host'});
					local $ok = $vu ? 1 : 0;
					print $outfd "2 $conv->{'user'} $ok $expired $notexist\n";
					&end_pam_conversation($conv);
					}
				}
			elsif ($inline =~ /^writesudo\s+(\S+)\s+(\d+)/) {
				# Store the fact that some user can sudo to root
				local ($user, $ok) = ($1, $2);
				$sudocache{$user} = $ok." ".time();
				}
			elsif ($inline =~ /^readsudo\s+(\S+)/) {
				# Query the user sudo cache (valid for 1 minute)
				local $user = $1;
				local ($ok, $last) =
					split(/\s+/, $sudocache{$user});
				if ($last < time()-60) {
					# Cache too old
					print $outfd "2\n";
					}
				else {
					# Tell client OK or not
					print $outfd "$ok\n";
					}
				}
			elsif ($inline =~ /\S/) {
				# Unknown line from pipe?
				print DEBUG "main: Unknown line from pipe $inline\n";
				print STDERR "Unknown line from pipe $inline\n";
				}
			else {
				# close pipe
				close($infd); close($outfd);
				$passin[$i] = $passout[$i] = undef;
				}
			}
		}
	@passin = grep { defined($_) } @passin;
	@passout = grep { defined($_) } @passout;
	}

# handle_request(remoteaddress, localaddress)
# Where the real work is done
sub handle_request
{
$acptip = inet_ntoa((unpack_sockaddr_in($_[0]))[1]);
$localip = $_[1] ? inet_ntoa((unpack_sockaddr_in($_[1]))[1]) : undef;
print DEBUG "handle_request: from $acptip to $localip\n";
if ($config{'loghost'}) {
	$acpthost = gethostbyaddr(inet_aton($acptip), AF_INET);
	$acpthost = $acptip if (!$acpthost);
	}
else {
	$acpthost = $acptip;
	}
$datestr = &http_date(time());
$ok_code = 200;
$ok_message = "Document follows";
$logged_code = undef;
$reqline = $request_uri = $page = undef;
$authuser = undef;
$validated = undef;

# check address against access list
if (@deny && &ip_match($acptip, $localip, @deny) ||
    @allow && !&ip_match($acptip, $localip, @allow)) {
	&http_error(403, "Access denied for $acptip");
	return 0;
	}

if ($use_libwrap) {
	# Check address with TCP-wrappers
	if (!hosts_ctl($config{'pam'}, STRING_UNKNOWN,
		       $acptip, STRING_UNKNOWN)) {
		&http_error(403, "Access denied for $acptip");
		return 0;
		}
	}
print DEBUG "handle_request: passed IP checks\n";

# Compute a timeout for the start of headers, based on the number of
# child processes. As this increases, we use a shorter timeout to avoid
# an attacker overloading the system.
local $header_timeout = 60 + ($config{'maxconns'} - @childpids) * 10;

# Wait at most 60 secs for start of headers for initial requests, or
# 10 minutes for kept-alive connections
local $rmask;
vec($rmask, fileno(SOCK), 1) = 1;
local $to = $checked_timeout ? 10*60 : $header_timeout;
local $sel = select($rmask, undef, undef, $to);
if (!$sel) {
	if ($checked_timeout) {
		print DEBUG "handle_request: exiting due to timeout of $to\n";
		exit;
		}
	else {
		&http_error(400, "Timeout",
			    "Waited for that $to seconds for start of headers");
		}
	}
$checked_timeout++;
print DEBUG "handle_request: passed timeout check\n";

# Read the HTTP request and headers
local $origreqline = &read_line();
($reqline = $origreqline) =~ s/\r|\n//g;
$method = $page = $request_uri = undef;
print DEBUG "handle_request reqline=$reqline\n";
if (!$reqline && (!$use_ssl || $checked_timeout > 1)) {
	# An empty request .. just close the connection
	print DEBUG "handle_request: rejecting empty request\n";
	return 0;
	}
elsif ($reqline !~ /^(\S+)\s+(.*)\s+HTTP\/1\..$/) {
	print DEBUG "handle_request: invalid reqline=$reqline\n";
	if ($use_ssl) {
		# This could be an http request when it should be https
		$use_ssl = 0;

		local $url = $config{'musthost'} ?
				"https://$config{'musthost'}:$port/" :
				"https://$localip:$port/";
 		
		if ($config{'ssl_redirect'}) {
			# Just re-direct to the correct URL
			&write_data("HTTP/1.0 302 Moved Temporarily\r\n");
			&write_data("Date: $datestr\r\n");
			&write_data("Server: $config{'server'}\r\n");
			&write_data("Location: $url\r\n");
			&write_keep_alive(0);
			&write_data("\r\n");
			return 0;
			}
		else {
			# Tell user the correct URL 			
			&http_error(200, "Bad Request", "here1: This web server is running in SSL mode. Try the URL <a href='$url'>$url</a> instead.<br>");
			}
		}
	elsif (ord(substr($reqline, 0, 1)) == 128 && !$use_ssl) {
		# This could be an https request when it should be http ..
		# need to fake a HTTP response
		eval <<'EOF';
			use Net::SSLeay;
			eval "Net::SSLeay::SSLeay_add_ssl_algorithms()";
			eval "Net::SSLeay::load_error_strings()";
			$ssl_ctx = Net::SSLeay::CTX_new();
			Net::SSLeay::CTX_use_RSAPrivateKey_file(
				$ssl_ctx, $config{'keyfile'},
				&Net::SSLeay::FILETYPE_PEM);
			Net::SSLeay::CTX_use_certificate_file(
				$ssl_ctx,
				$config{'certfile'} || $config{'keyfile'},
				&Net::SSLeay::FILETYPE_PEM);
			$ssl_con = Net::SSLeay::new($ssl_ctx);
			pipe(SSLr, SSLw);
			if (!fork()) {
				close(SSLr);
				select(SSLw); $| = 1; select(STDOUT);
				print SSLw $origreqline;
				local $buf;
				while(sysread(SOCK, $buf, 1) > 0) {
					print SSLw $buf;
					}
				close(SOCK);
				exit;
				}
			close(SSLw);
			Net::SSLeay::set_wfd($ssl_con, fileno(SOCK));
			Net::SSLeay::set_rfd($ssl_con, fileno(SSLr));
			Net::SSLeay::accept($ssl_con) || die "accept() failed";
			$use_ssl = 1;
			local $url = $config{'musthost'} ?
					"https://$config{'musthost'}:$port/" :
					"https://$localip:$port/";
			if ($config{'ssl_redirect'}) {
				# Just re-direct to the correct URL
				&write_data("HTTP/1.0 302 Moved Temporarily\r\n");
				&write_data("Date: $datestr\r\n");
				&write_data("Server: $config{'server'}\r\n");
				&write_data("Location: $url\r\n");
				&write_keep_alive(0);
				&write_data("\r\n");
				return 0;
				}
			else {
				# Tell user the correct URL
				
				&http_error(200, "Bad Request", "here2: This web server is not running in SSL mode. Try the URL <a href='$url'>$url</a> instead.<br>");
				}
EOF
		if ($@) {
			&http_error(400, "Bad Request");
			}
		}
	else {
		&http_error(400, "Bad Request");
		}
	}
$method = $1;
$request_uri = $page = $2;
%header = ();
local $lastheader;
while(1) {
	($headline = &read_line()) =~ s/\r|\n//g;
	last if ($headline eq "");
	print DEBUG "handle_request: got headline $headline\n";
	if ($headline =~ /^(\S+):\s*(.*)$/) {
		$header{$lastheader = lc($1)} = $2;
		}
	elsif ($headline =~ /^\s+(.*)$/) {
		$header{$lastheader} .= $headline;
		}
	else {
		&http_error(400, "Bad Header $headline");
		}
	}
if (defined($header{'host'})) {
	if ($header{'host'} =~ /^([^:]+):([0-9]+)$/) { $host = $1; $port = $2; }
	else { $host = $header{'host'}; }
	if ($config{'musthost'} && $host ne $config{'musthost'}) {
		# Disallowed hostname used
		&http_error(400, "Invalid HTTP hostname");
		}
	}
undef(%in);
if ($page =~ /^([^\?]+)\?(.*)$/) {
	# There is some query string information
	$page = $1;
	$querystring = $2;
	print DEBUG "handle_request: querystring=$querystring\n";
	if ($querystring !~ /=/) {
		$queryargs = $querystring;
		$queryargs =~ s/\+/ /g;
    		$queryargs =~ s/%(..)/pack("c",hex($1))/ge;
		$querystring = "";
		}
	else {
		# Parse query-string parameters
		local @in = split(/\&/, $querystring);
		foreach $i (@in) {
			local ($k, $v) = split(/=/, $i, 2);
			$k =~ s/\+/ /g; $k =~ s/%(..)/pack("c",hex($1))/ge;
			$v =~ s/\+/ /g; $v =~ s/%(..)/pack("c",hex($1))/ge;
			$in{$k} = $v;
			}
		}
	}
$posted_data = undef;
if ($method eq 'POST' &&
    $header{'content-type'} eq 'application/x-www-form-urlencoded') {
	# Read in posted query string information, up the configured maximum
	# post request length
	$clen = $header{"content-length"};
	$clen_read = $clen > $config{'max_post'} ? $config{'max_post'} : $clen;
	while(length($posted_data) < $clen_read) {
		$buf = &read_data($clen_read - length($posted_data));
		if (!length($buf)) {
			&http_error(500, "Failed to read POST request");
			}
		chomp($posted_data);
		$posted_data =~ s/\015$//mg;
		$posted_data .= $buf;
		}
	print DEBUG "clen_read=$clen_read clen=$clen posted_data=",length($posted_data),"\n";
	if ($clen_read != $clen && length($posted_data) > $clen) {
		# If the client sent more data than we asked for, chop the
		# rest off
		$posted_data = substr($posted_data, 0, $clen);
		}
	if ($header{'user-agent'} =~ /MSIE/ &&
	    $header{'user-agent'} !~ /Opera/i) {
		# MSIE includes an extra newline in the data
		$posted_data =~ s/\r|\n//g;
		}
	local @in = split(/\&/, $posted_data);
	foreach $i (@in) {
		local ($k, $v) = split(/=/, $i, 2);
		#$v =~ s/\r|\n//g;
		$k =~ s/\+/ /g; $k =~ s/%(..)/pack("c",hex($1))/ge;
		$v =~ s/\+/ /g; $v =~ s/%(..)/pack("c",hex($1))/ge;
		$in{$k} = $v;
		}
	print DEBUG "handle_request: posted_data=$posted_data\n";
	}

# replace %XX sequences in page
$page =~ s/%(..)/pack("c",hex($1))/ge;

# Check if the browser's user agent indicates a mobile device
$mobile_device = &is_mobile_useragent($header{'user-agent'});

# Check if Host: header is for a mobile URL
foreach my $m (@mobile_prefixes) {
	if ($header{'host'} =~ /^\Q$m\E/i) {
		$mobile_device = 1;
		}
	}

# check for the logout flag file, and if existant deny authentication
if ($config{'logout'} && -r $config{'logout'}.$in{'miniserv_logout_id'}) {
	print DEBUG "handle_request: logout flag set\n";
	$deny_authentication++;
	open(LOGOUT, $config{'logout'}.$in{'miniserv_logout_id'});
	chop($count = <LOGOUT>);
	close(LOGOUT);
	$count--;
	if ($count > 0) {
		open(LOGOUT, ">$config{'logout'}$in{'miniserv_logout_id'}");
		print LOGOUT "$count\n";
		close(LOGOUT);
		}
	else {
		unlink($config{'logout'}.$in{'miniserv_logout_id'});
		}
	}

# check for any redirect for the requested URL
foreach my $pfx (@strip_prefix) {
	my $l = length($pfx);
	if(length($page) >= $l &&
	   substr($page,0,$l) eq $pfx) {
		$page=substr($page,$l);
		last;
		}
	}
$simple = &simplify_path($page, $bogus);
$rpath = $simple;
$rpath .= "&".$querystring if (defined($querystring));
$redir = $redirect{$rpath};
if (defined($redir)) {
	print DEBUG "handle_request: redir=$redir\n";
	&write_data("HTTP/1.0 302 Moved Temporarily\r\n");
	&write_data("Date: $datestr\r\n");
	&write_data("Server: $config{'server'}\r\n");
	local $ssl = $use_ssl || $config{'inetd_ssl'};
	$portstr = $port == 80 && !$ssl ? "" :
		   $port == 443 && $ssl ? "" : ":$port";
	$prot = $ssl ? "https" : "http";
	&write_data("Location: $prot://$host$portstr$redir\r\n");
	&write_keep_alive(0);
	&write_data("\r\n");
	return 0;
	}

# Check for a DAV request
$davpath = undef;
foreach my $d (@davpaths) {
	if ($simple eq $d || $simple =~ /^\Q$d\E\//) {
		$davpath = $d;
		last;
		}
	}
if (!$davpath && ($method eq "SEARCH" || $method eq "PUT")) {
	&http_error(400, "Bad Request method $method");
	}

# Check for password if needed
if (%users) {
	print DEBUG "handle_request: Need authentication\n";
	$validated = 0;
	$blocked = 0;

	# Session authentication is never used for connections by
	# another webmin server, or for specified pages, or for DAV, or XMLRPC,
	# or mobile browsers if requested.
	if ($header{'user-agent'} =~ /webmin/i ||
	    $header{'user-agent'} =~ /$config{'agents_nosession'}/i ||
	    $sessiononly{$simple} || $davpath ||
	    $simple eq "/xmlrpc.cgi" ||
            $acptip eq $config{'host_nosession'} ||
	    $mobile_device && $config{'mobile_nosession'}) {
		print DEBUG "handle_request: Forcing HTTP authentication\n";
		$config{'session'} = 0;
		}

	# check for SSL authentication
	if ($use_ssl && $verified_client) {
		$peername = Net::SSLeay::X509_NAME_oneline(
				Net::SSLeay::X509_get_subject_name(
					Net::SSLeay::get_peer_certificate(
						$ssl_con)));
		local $peername2 = $peername;
		$peername2 =~ s/Email=/emailAddress=/ ||
			$peername2 =~ s/emailAddress=/Email=/;
		foreach $u (keys %certs) {
			if ($certs{$u} eq $peername ||
			    $certs{$u} eq $peername2) {
				$authuser = $u;
				$validated = 2;
				#syslog("info", "%s", "SSL login as $authuser from $acpthost") if ($use_syslog);
				last;
				}
			}
		if ($use_syslog && !$validated) {
			syslog("crit", "%s",
			       "Unknown SSL certificate $peername");
			}
		}

	if (!$validated && !$deny_authentication) {
		# check for IP-based authentication
		local $a;
		foreach $a (keys %ipaccess) {
			if ($acptip eq $a) {
				# It does! Auth as the user
				$validated = 3;
				$baseauthuser = $authuser =
					$ipaccess{$a};
				}
			}
		}

	# Check for normal HTTP authentication
	if (!$validated && !$deny_authentication && !$config{'session'} &&
	    $header{authorization} =~ /^basic\s+(\S+)$/i) {
		# authorization given..
		($authuser, $authpass) = split(/:/, &b64decode($1), 2);
		print DEBUG "handle_request: doing basic auth check authuser=$authuser authpass=$authpass\n";
		local ($vu, $expired, $nonexist) =
			&validate_user($authuser, $authpass, $host);
		print DEBUG "handle_request: vu=$vu expired=$expired nonexist=$nonexist\n";
		if ($vu && (!$expired || $config{'passwd_mode'} == 1)) {
			$authuser = $vu;
			$validated = 1;
			}
		else {
			$validated = 0;
			}
		if ($use_syslog && !$validated) {
			syslog("crit", "%s",
			       ($nonexist ? "Non-existent" :
				$expired ? "Expired" : "Invalid").
			       " login as $authuser from $acpthost");
			}
		if ($authuser =~ /\r|\n|\s/) {
			&http_error(500, "Invalid username",
				    "Username contains invalid characters");
			}
		if ($authpass =~ /\r|\n/) {
			&http_error(500, "Invalid password",
				    "Password contains invalid characters");
			}

		if ($config{'passdelay'} && !$config{'inetd'}) {
			# check with main process for delay
			print DEBUG "handle_request: about to ask for password delay\n";
			print $PASSINw "delay $authuser $acptip $validated\n";
			<$PASSOUTr> =~ /(\d+) (\d+)/;
			$blocked = $2;
			print DEBUG "handle_request: password delay $1 $2\n";
			sleep($1);
			}
		}

	# Check for a visit to the special session login page
	if ($config{'session'} && !$deny_authentication &&
	    $page eq $config{'session_login'}) {
		if ($in{'logout'} && $header{'cookie'} =~ /(^|\s)$sidname=([a-f0-9]+)/) {
			# Logout clicked .. remove the session
			local $sid = $2;
			print $PASSINw "delete $sid\n";
			local $louser = <$PASSOUTr>;
			chop($louser);
			$logout = 1;
			$already_session_id = undef;
			$authuser = $baseauthuser = undef;
			if ($louser) {
				if ($use_syslog) {
					syslog("info", "%s", "Logout by $louser from $acpthost");
					}
				&run_logout_script($louser, $sid,
						   $acptip, $localip);
				&write_logout_utmp($louser, $actphost);
				}
			}
		else {
			# Validate the user
			if ($in{'user'} =~ /\r|\n|\s/) {
				&http_error(500, "Invalid username",
				    "Username contains invalid characters");
				}
			if ($in{'pass'} =~ /\r|\n/) {
				&http_error(500, "Invalid password",
				    "Password contains invalid characters");
				}

			local ($vu, $expired, $nonexist) =
				&validate_user($in{'user'}, $in{'pass'}, $host);
			local $hrv = &handle_login(
					$vu || $in{'user'}, $vu ? 1 : 0,
				      	$expired, $nonexist, $in{'pass'});
			return $hrv if (defined($hrv));
			}
		}

	# Check for a visit to the special PAM login page
	if ($config{'session'} && !$deny_authentication &&
	    $use_pam && $config{'pam_conv'} && $page eq $config{'pam_login'} &&
	    !$in{'restart'}) {
		# A question has been entered .. submit it to the main process
		print DEBUG "handle_request: Got call to $page ($in{'cid'})\n";
		print DEBUG "handle_request: For PAM, authuser=$authuser\n";
		if ($in{'answer'} =~ /\r|\n/ || $in{'cid'} =~ /\r|\n|\s/) {
			&http_error(500, "Invalid response",
			    "Response contains invalid characters");
			}

		if (!$in{'cid'}) {
			# Start of a new conversation - answer must be username
			$cid = &generate_random_id($in{'answer'});
			print $PASSINw "pamstart $cid $host $in{'answer'}\n";
			}
		else {
			# A response to a previous question
			$cid = $in{'cid'};
			print $PASSINw "pamanswer $cid $in{'answer'}\n";
			}

		# Read back the response, and the next question (if any)
		local $line = <$PASSOUTr>;
		$line =~ s/\r|\n//g;
		local ($rv, $question) = split(/\s+/, $line, 2);
		if ($rv == 0) {
			# Cannot login!
			local $hrv = &handle_login(
				$in{'answer'} || "unknown", 0, 0, 1, undef);
			return $hrv if (defined($hrv));
			}
		elsif ($rv == 1 || $rv == 3) {
			# Another question .. force use of PAM CGI
			$validated = 1;
			$method = "GET";
			$querystring .= "&cid=$cid&question=".
					&urlize($question);
			$querystring .= "&password=1" if ($rv == 3);
			$queryargs = "";
			$page = $config{'pam_login'};
			$miniserv_internal = 1;
			$logged_code = 401;
			}
		elsif ($rv == 2) {
			# Got back a final ok or failure
			local ($user, $ok, $expired, $nonexist) =
				split(/\s+/, $question);
			local $hrv = &handle_login(
				$user, $ok, $expired, $nonexist, undef);
			return $hrv if (defined($hrv));
			}
		elsif ($rv == 4) {
			# A message from PAM .. tell the user
			$validated = 1;
			$method = "GET";
			$querystring .= "&cid=$cid&message=".
					&urlize($question);
			$queryargs = "";
			$page = $config{'pam_login'};
			$miniserv_internal = 1;
			$logged_code = 401;
			}
		}

	# Check for a visit to the special password change page
	if ($config{'session'} && !$deny_authentication &&
	    $page eq $config{'password_change'} && !$validated &&
	    $config{'passwd_mode'} == 2) {
		# Just let this slide ..
		$validated = 1;
		$miniserv_internal = 3;
		}

	# Check for an existing session
	if ($config{'session'} && !$validated) {
		if ($already_session_id) {
			$session_id = $already_session_id;
			$authuser = $already_authuser;
			$validated = 1;
			}
		elsif (!$deny_authentication &&
		       $header{'cookie'} =~ /(^|\s)$sidname=([a-f0-9]+)/) {
			$session_id = $2;
			local $notimeout = $in{'webmin_notimeout'} ? 1 : 0;
			print $PASSINw "verify $session_id $notimeout\n";
			<$PASSOUTr> =~ /(\d+)\s+(\S+)/;
			if ($1 == 2) {
				# Valid session continuation
				$validated = 1;
				$authuser = $2;
				#$already_session_id = $session_id;
				$already_authuser = $authuser;
				}
			elsif ($1 == 1) {
				# Session timed out
				$timed_out = $2;
				}
			else {
				# Invalid session ID .. don't set verified
				}
			}
		}

	# Check for local authentication
	if ($localauth_user && !$header{'x-forwarded-for'} && !$header{'via'}) {
		if (defined($users{$localauth_user})) {
			# Local user exists in webmin users file
			$validated = 1;
			$authuser = $localauth_user;
			}
		else {
			# Check if local user is allowed by unixauth
			local @can = &can_user_login($localauth_user,
						     undef, $host);
			if ($can[0]) {
				$validated = 2;
				$authuser = $localauth_user;
				}
			else {
				$localauth_user = undef;
				}
			}
		}

	if (!$validated) {
		# Check if this path allows anonymous access
		local $a;
		foreach $a (keys %anonymous) {
			if (substr($simple, 0, length($a)) eq $a) {
				# It does! Auth as the user, if IP access
				# control allows him.
				if (&check_user_ip($anonymous{$a}) &&
				    &check_user_time($anonymous{$a})) {
					$validated = 3;
					$baseauthuser = $authuser =
						$anonymous{$a};
					}
				}
			}
		}

	if (!$validated) {
		# Check if this path allows unauthenticated access
		local ($u, $unauth);
		foreach $u (@unauth) {
			$unauth++ if ($simple =~ /$u/);
			}
		if (!$bogus && $unauth) {
			# Unauthenticated directory or file request - approve it
			$validated = 4;
			$baseauthuser = $authuser = undef;
			}
		}

	if (!$validated) {
		if ($blocked == 0) {
			# No password given.. ask
			if ($config{'pam_conv'} && $use_pam) {
				# Force CGI for PAM question, starting with
				# the username which is always needed
				$validated = 1;
				$method = "GET";
				$querystring .= "&initial=1&question=".
						&urlize("Username");
				$querystring .= "&failed=$failed_user" if ($failed_user);
				$querystring .= "&timed_out=$timed_out" if ($timed_out);
				$queryargs = "";
				$page = $config{'pam_login'};
				$miniserv_internal = 1;
				$logged_code = 401;
				}
			elsif ($config{'session'}) {
				# Force CGI for session login
				$validated = 1;
				if ($logout) {
					$querystring .= "&logout=1&page=/";
					}
				else {
					# Re-direct to current module only
					local $rpage = $request_uri;
					if (!$config{'loginkeeppage'}) {
						$rpage =~ s/\?.*$//;
						$rpage =~ s/[^\/]+$//
						}
					$querystring = "page=".&urlize($rpage);
					}
				$method = "GET";
				$querystring .= "&failed=$failed_user" if ($failed_user);
				$querystring .= "&timed_out=$timed_out" if ($timed_out);
				$queryargs = "";
				$page = $config{'session_login'};
				$miniserv_internal = 1;
				$logged_code = 401;
				}
			else {
				# Ask for login with HTTP authentication
				&write_data("HTTP/1.0 401 Unauthorized\r\n");
				&write_data("Date: $datestr\r\n");
				&write_data("Server: $config{'server'}\r\n");
				&write_data("WWW-authenticate: Basic ".
					   "realm=\"$config{'realm'}\"\r\n");
				&write_keep_alive(0);
				&write_data("Content-type: text/html\r\n");
				&write_data("\r\n");
				&reset_byte_count();
				&write_data("<html>\n");
				&write_data("<head><title>Unauthorized</title></head>\n");
				&write_data("<body><h1>Unauthorized</h1>\n");
				&write_data("A password is required to access this\n");
				&write_data("web server. Please try again. <p>\n");
				&write_data("</body></html>\n");
				&log_request($acpthost, undef, $reqline, 401, &byte_count());
				return 0;
				}
			}
		elsif ($blocked == 1) {
			# when the host has been blocked, give it an error
			&http_error(403, "Access denied for $acptip. The host ".
					 "has been blocked because of too ".
					 "many authentication failures.");
			}
		elsif ($blocked == 2) {
			# when the user has been blocked, give it an error
			&http_error(403, "Access denied. The user ".
					 "has been blocked because of too ".
					 "many authentication failures.");
			}
		}
	else {
		# Get the real Webmin username
		local @can = &can_user_login($authuser, undef, $host);
		$baseauthuser = $can[3] || $authuser;

		if ($config{'remoteuser'} && !$< && $validated) {
			# Switch to the UID of the remote user (if he exists)
			local @u = getpwnam($authuser);
			if (@u && $< != $u[2]) {
				$( = $u[3]; $) = "$u[3] $u[3]";
				($>, $<) = ($u[2], $u[2]);
				}
			else {
				&http_error(500, "Unix user $authuser does not exist");
				return 0;
				}
			}
		}

	# Check per-user IP access control
	if (!&check_user_ip($baseauthuser)) {
		&http_error(403, "Access denied for $acptip");
		return 0;
		}

	# Check per-user allowed times
	if (!&check_user_time($baseauthuser)) {
		&http_error(403, "Access denied at the current time");
		return 0;
		}
	}

# Validate the path, and convert to canonical form
rerun:
$simple = &simplify_path($page, $bogus);
print DEBUG "handle_request: page=$page simple=$simple\n";
if ($bogus) {
	&http_error(400, "Invalid path");
	}

# Check for a DAV request
if ($davpath) {
	return &handle_dav_request($davpath);
	}

# Work out the active theme
local $preroot = $mobile_device && defined($config{'mobile_preroot'}) ?
			$config{'mobile_preroot'} :
		 $authuser && defined($config{'preroot_'.$authuser}) ?
			$config{'preroot_'.$authuser} :
		 $authuser && $baseauthuser &&
		     defined($config{'preroot_'.$baseauthuser}) ?
		 	$config{'preroot_'.$baseauthuser} :
			$config{'preroot'};

# Look for the file under the roots
local ($full, @stfull);
if ($preroot) {
	# Always under the current webmin root
	$preroot =~ s/^.*\///g;
	$preroot = $roots[0].'/'.$preroot;
	}
$foundroot = undef;
if ($preroot) {
	# Look in the theme root directory first
	$is_directory = 1;
	$sofar = "";
	$full = $preroot.$sofar;
	$scriptname = $simple;
	foreach $b (split(/\//, $simple)) {
		if ($b ne "") { $sofar .= "/$b"; }
		$full = $preroot.$sofar;
		@stfull = stat($full);
		if (!@stfull) { undef($full); last; }

		# Check if this is a directory
		if (-d _) {
			# It is.. go on parsing
			$is_directory = 1;
			next;
			}
		else { $is_directory = 0; }

		# Check if this is a CGI program
		if (&get_type($full) eq "internal/cgi") {
			$pathinfo = substr($simple, length($sofar));
			$pathinfo .= "/" if ($page =~ /\/$/);
			$scriptname = $sofar;
			last;
			}
		}
	if ($full) {
		# Found it!
		if ($sofar eq '') {
			$cgi_pwd = $roots[0];
			}
		elsif ($is_directory) {
			$cgi_pwd = "$roots[0]$sofar";
			}
		else {
			"$roots[0]$sofar" =~ /^(.*\/)[^\/]+$/;
			$cgi_pwd = $1;
			}
		$foundroot = $preroot;
		if ($is_directory) {
			# Check for index files in the directory
			local $foundidx;
			foreach $idx (split(/\s+/, $config{"index_docs"})) {
				$idxfull = "$full/$idx";
				local @stidxfull = stat($idxfull);
				if (-r _ && !-d _) {
					$full = $idxfull;
					@stfull = @stidxfull;
					$is_directory = 0;
					$scriptname .= "/"
						if ($scriptname ne "/");
					$foundidx++;
					last;
					}
				}
			@stfull = stat($full) if (!$foundidx);
			}
		}
	}
print DEBUG "handle_request: initial full=$full\n";

# Look in the real root directories, stopping when we find a file or directory
if (!$full || $is_directory) {
	ROOT: foreach $root (@roots) {
		$sofar = "";
		$full = $root.$sofar;
		$scriptname = $simple;
		foreach $b ($simple eq "/" ? ( "" ) : split(/\//, $simple)) {
			if ($b ne "") { $sofar .= "/$b"; }
			$full = $root.$sofar;
			@stfull = stat($full);
			if (!@stfull) {
				next ROOT;
				}

			# Check if this is a directory
			if (-d _) {
				# It is.. go on parsing
				next;
				}

			# Check if this is a CGI program
			if (&get_type($full) eq "internal/cgi") {
				$pathinfo = substr($simple, length($sofar));
				$pathinfo .= "/" if ($page =~ /\/$/);
				$scriptname = $sofar;
				last;
				}
			}

		# Run CGI in the same directory as whatever file
		# was requested
		$full =~ /^(.*\/)[^\/]+$/; $cgi_pwd = $1;

		if (-e $full) {
			# Found something!
			$realroot = $root;
			$foundroot = $root;
			last;
			}
		}
	if (!@stfull) { &http_error(404, "File not found"); }
	}
print DEBUG "handle_request: full=$full\n";
@stfull = stat($full) if (!@stfull);

# check filename against denyfile regexp
local $denyfile = $config{'denyfile'};
if ($denyfile && $full =~ /$denyfile/) {
	&http_error(403, "Access denied to $page");
	return 0;
	}

# Reached the end of the path OK.. see what we've got
if (-d _) {
	# See if the URL ends with a / as it should
	print DEBUG "handle_request: found a directory\n";
	if ($page !~ /\/$/) {
		# It doesn't.. redirect
		&write_data("HTTP/1.0 302 Moved Temporarily\r\n");
		$ssl = $use_ssl || $config{'inetd_ssl'};
		$portstr = $port == 80 && !$ssl ? "" :
			   $port == 443 && $ssl ? "" : ":$port";
		&write_data("Date: $datestr\r\n");
		&write_data("Server: $config{server}\r\n");
		$prot = $ssl ? "https" : "http";
		&write_data("Location: $prot://$host$portstr$page/\r\n");
		&write_keep_alive(0);
		&write_data("\r\n");
		&log_request($acpthost, $authuser, $reqline, 302, 0);
		return 0;
		}
	# A directory.. check for index files
	local $foundidx;
	foreach $idx (split(/\s+/, $config{"index_docs"})) {
		$idxfull = "$full/$idx";
		@stidxfull = stat($idxfull);
		if (-r _ && !-d _) {
			$cgi_pwd = $full;
			$full = $idxfull;
			@stfull = @stidxfull;
			$scriptname .= "/" if ($scriptname ne "/");
			$foundidx++;
			last;
			}
		}
	@stfull = stat($full) if (!$foundidx);
	}
if (-d _) {
	# This is definately a directory.. list it
	print DEBUG "handle_request: listing directory\n";
	&write_data("HTTP/1.0 $ok_code $ok_message\r\n");
	&write_data("Date: $datestr\r\n");
	&write_data("Server: $config{server}\r\n");
	&write_data("Content-type: text/html\r\n");
	&write_keep_alive(0);
	&write_data("\r\n");
	&reset_byte_count();
	&write_data("<h1>Index of $simple</h1>\n");
	&write_data("<pre>\n");
	&write_data(sprintf "%-35.35s %-20.20s %-10.10s\n",
			"Name", "Last Modified", "Size");
	&write_data("<hr>\n");
	opendir(DIR, $full);
	while($df = readdir(DIR)) {
		if ($df =~ /^\./) { next; }
		$fulldf = $full eq "/" ? $full.$df : $full."/".$df;
		(@stbuf = stat($fulldf)) || next;
		if (-d _) { $df .= "/"; }
		@tm = localtime($stbuf[9]);
		$fdate = sprintf "%2.2d/%2.2d/%4.4d %2.2d:%2.2d:%2.2d",
				$tm[3],$tm[4]+1,$tm[5]+1900,
				$tm[0],$tm[1],$tm[2];
		$len = length($df); $rest = " "x(35-$len);
		&write_data(sprintf 
		 "<a href=\"%s\">%-${len}.${len}s</a>$rest %-20.20s %-10.10s\n",
		 $df, $df, $fdate, $stbuf[7]);
		}
	closedir(DIR);
	&log_request($acpthost, $authuser, $reqline, $ok_code, &byte_count());
	return 0;
	}

# CGI or normal file
local $rv;
if (&get_type($full) eq "internal/cgi" && $validated != 4) {
	# A CGI program to execute
	print DEBUG "handle_request: executing CGI\n";
	$envtz = $ENV{"TZ"};
	$envuser = $ENV{"USER"};
	$envpath = $ENV{"PATH"};
	$envlang = $ENV{"LANG"};
	$envroot = $ENV{"SystemRoot"};
	foreach my $k (keys %ENV) {
		delete($ENV{$k});
		}
	$ENV{"PATH"} = $envpath if ($envpath);
	$ENV{"TZ"} = $envtz if ($envtz);
	$ENV{"USER"} = $envuser if ($envuser);
	$ENV{"OLD_LANG"} = $envlang if ($envlang);
	$ENV{"SystemRoot"} = $envroot if ($envroot);
	$ENV{"HOME"} = $user_homedir;
	$ENV{"SERVER_SOFTWARE"} = $config{"server"};
	$ENV{"SERVER_NAME"} = $host;
	$ENV{"SERVER_ADMIN"} = $config{"email"};
	$ENV{"SERVER_ROOT"} = $roots[0];
	$ENV{"SERVER_REALROOT"} = $realroot;
	$ENV{"SERVER_PORT"} = $port;
	$ENV{"REMOTE_HOST"} = $acpthost;
	$ENV{"REMOTE_ADDR"} = $acptip;
	$ENV{"REMOTE_USER"} = $authuser;
	$ENV{"BASE_REMOTE_USER"} = $authuser ne $baseauthuser ?
					$baseauthuser : undef;
	$ENV{"REMOTE_PASS"} = $authpass if (defined($authpass) &&
					    $config{'pass_password'});
	print DEBUG "REMOTE_USER = ",$ENV{"REMOTE_USER"},"\n";
	print DEBUG "BASE_REMOTE_USER = ",$ENV{"BASE_REMOTE_USER"},"\n";
	$ENV{"SSL_USER"} = $peername if ($validated == 2);
	$ENV{"ANONYMOUS_USER"} = "1" if ($validated == 3 || $validated == 4);
	$ENV{"DOCUMENT_ROOT"} = $roots[0];
	$ENV{"DOCUMENT_REALROOT"} = $realroot;
	$ENV{"GATEWAY_INTERFACE"} = "CGI/1.1";
	$ENV{"SERVER_PROTOCOL"} = "HTTP/1.0";
	$ENV{"REQUEST_METHOD"} = $method;
	$ENV{"SCRIPT_NAME"} = $scriptname;
	$ENV{"SCRIPT_FILENAME"} = $full;
	$ENV{"REQUEST_URI"} = $request_uri;
	$ENV{"PATH_INFO"} = $pathinfo;
	if ($pathinfo) {
		$ENV{"PATH_TRANSLATED"} = "$roots[0]$pathinfo";
		$ENV{"PATH_REALTRANSLATED"} = "$realroot$pathinfo";
		}
	$ENV{"QUERY_STRING"} = $querystring;
	$ENV{"MINISERV_CONFIG"} = $config_file;
	$ENV{"HTTPS"} = "ON" if ($use_ssl || $config{'inetd_ssl'});
	$ENV{"SESSION_ID"} = $session_id if ($session_id);
	$ENV{"LOCAL_USER"} = $localauth_user if ($localauth_user);
	$ENV{"MINISERV_INTERNAL"} = $miniserv_internal if ($miniserv_internal);
	if (defined($header{"content-length"})) {
		$ENV{"CONTENT_LENGTH"} = $header{"content-length"};
		}
	if (defined($header{"content-type"})) {
		$ENV{"CONTENT_TYPE"} = $header{"content-type"};
		}
	foreach $h (keys %header) {
		($hname = $h) =~ tr/a-z/A-Z/;
		$hname =~ s/\-/_/g;
		$ENV{"HTTP_$hname"} = $header{$h};
		}
	$ENV{"PWD"} = $cgi_pwd;
	foreach $k (keys %config) {
		if ($k =~ /^env_(\S+)$/) {
			$ENV{$1} = $config{$k};
			}
		}
	delete($ENV{'HTTP_AUTHORIZATION'});
	$ENV{'HTTP_COOKIE'} =~ s/;?\s*$sidname=([a-f0-9]+)//;
	$ENV{'MOBILE_DEVICE'} = 1 if ($mobile_device);

	# Check if the CGI can be handled internally
	open(CGI, $full);
	local $first = <CGI>;
	close(CGI);
	$first =~ s/[#!\r\n]//g;
	$nph_script = ($full =~ /\/nph-([^\/]+)$/);
	seek(STDERR, 0, 2);
	if (!$config{'forkcgis'} &&
	    ($first eq $perl_path || $first eq $linked_perl_path) &&
	      $] >= 5.004 ||
            $config{'internalcgis'}) {
		# setup environment for eval
		chdir($ENV{"PWD"});
		@ARGV = split(/\s+/, $queryargs);
		$0 = $full;
		if ($posted_data) {
			# Already read the post input
			$postinput = $posted_data;
			}
		$clen = $header{"content-length"};
		$SIG{'CHLD'} = 'DEFAULT';
		eval {
			# Have SOCK closed if the perl exec's something
			use Fcntl;
			fcntl(SOCK, F_SETFD, FD_CLOEXEC);
			};
		#shutdown(SOCK, 0);

		if ($config{'log'}) {
			open(MINISERVLOG, ">>$config{'logfile'}");
			if ($config{'logperms'}) {
				chmod(oct($config{'logperms'}),
				      $config{'logfile'});
				}
			else {
				chmod(0600, $config{'logfile'});
				}
			}
		$doing_eval = 1;
		$main_process_id = $$;
		$pkg = "main";
		if ($config{'eval_package'}) {
			# Eval in package from Webmin module name
			if ($full =~ /^\Q$foundroot\E\/([^\/]+)\//) {
				$pkg = $1;
				$pkg =~ s/[^A-Za-z0-9]/_/g;
				}
			}
		eval "
			\%pkg::ENV = \%ENV;
			package $pkg;
			tie(*STDOUT, 'miniserv');
			tie(*STDIN, 'miniserv');
			do \$miniserv::full;
			die \$@ if (\$@);
			";
		$doing_eval = 0;
		if ($@) {
			# Error in perl!
			&http_error(500, "Perl execution failed",
				    $config{'noshowstderr'} ? undef : $@);
			}
		elsif (!$doneheaders && !$nph_script) {
			&http_error(500, "Missing Headers");
			}
		$rv = 0;
		}
	else {
		$infile = undef;
		if (!$on_windows) {
			# fork the process that actually executes the CGI
			pipe(CGIINr, CGIINw);
			pipe(CGIOUTr, CGIOUTw);
			pipe(CGIERRr, CGIERRw);
			if (!($cgipid = fork())) {
				@execargs = ( $full, split(/\s+/, $queryargs) );
				chdir($ENV{"PWD"});
				close(SOCK);
				open(STDIN, "<&CGIINr");
				open(STDOUT, ">&CGIOUTw");
				open(STDERR, ">&CGIERRw");
				close(CGIINw); close(CGIOUTr); close(CGIERRr);
				exec(@execargs) ||
					die "Failed to exec $full : $!\n";
				exit(0);
				}
			close(CGIINr); close(CGIOUTw); close(CGIERRw);
			}
		else {
			# write CGI input to a temp file
			$infile = "$config{'tempbase'}.$$";
			open(CGIINw, ">$infile");
			# NOT binary mode, as CGIs don't read in it!
			}

		# send post data
		if ($posted_data) {
			# already read the posted data
			print CGIINw $posted_data;
			}
		$clen = $header{"content-length"};
		if ($method eq "POST" && $clen_read < $clen) {
			$SIG{'PIPE'} = 'IGNORE';
			$got = $clen_read;
			while($got < $clen) {
				$buf = &read_data($clen-$got);
				if (!length($buf)) {
					kill('TERM', $cgipid);
					unlink($infile) if ($infile);
					&http_error(500, "Failed to read ".
							 "POST request");
					}
				$got += length($buf);
				local ($wrote) = (print CGIINw $buf);
				last if (!$wrote);
				}
			# If the CGI terminated early, we still need to read
			# from the browser and throw away
			while($got < $clen) {
				$buf = &read_data($clen-$got);
				if (!length($buf)) {
					kill('TERM', $cgipid);
					unlink($infile) if ($infile);
					&http_error(500, "Failed to read ".
							 "POST request");
					}
				$got += length($buf);
				}
			$SIG{'PIPE'} = 'DEFAULT';
			}
		close(CGIINw);
		shutdown(SOCK, 0);

		if ($on_windows) {
			# Run the CGI program, and feed it input
			chdir($ENV{"PWD"});
			if ($first =~ /(perl|perl.exe)$/i) {
				# On Windows, run with Perl
				open(CGIOUTr, "$perl_path \"$full\" $queryargs <$infile |");
				}
			else {
				open(CGIOUTr, "\"$full\" $queryargs <$infile |");
				}
			binmode(CGIOUTr);
			}

		if (!$nph_script) {
			# read back cgi headers
			select(CGIOUTr); $|=1; select(STDOUT);
			$got_blank = 0;
			while(1) {
				$line = <CGIOUTr>;
				$line =~ s/\r|\n//g;
				if ($line eq "") {
					if ($got_blank || %cgiheader) { last; }
					$got_blank++;
					next;
					}
				if ($line !~ /^(\S+):\s+(.*)$/) {
					$errs = &read_errors(CGIERRr);
					close(CGIOUTr); close(CGIERRr);
					unlink($infile) if ($infile);
					&http_error(500, "Bad Header", $errs);
					}
				$cgiheader{lc($1)} = $2;
				push(@cgiheader, [ $1, $2 ]);
				}
			if ($cgiheader{"location"}) {
				&write_data("HTTP/1.0 302 Moved Temporarily\r\n");
				&write_data("Date: $datestr\r\n");
				&write_data("Server: $config{'server'}\r\n");
				&write_keep_alive(0);
				# ignore the rest of the output. This is a hack,
				# but is necessary for IE in some cases :(
				close(CGIOUTr); close(CGIERRr);
				}
			elsif ($cgiheader{"content-type"} eq "") {
				close(CGIOUTr); close(CGIERRr);
				unlink($infile) if ($infile);
				$errs = &read_errors(CGIERRr);
				&http_error(500, "Missing Content-Type Header",
				    $config{'noshowstderr'} ? undef : $errs);
				}
			else {
				&write_data("HTTP/1.0 $ok_code $ok_message\r\n");
				&write_data("Date: $datestr\r\n");
				&write_data("Server: $config{'server'}\r\n");
				&write_keep_alive(0);
				}
			foreach $h (@cgiheader) {
				&write_data("$h->[0]: $h->[1]\r\n");
				}
			&write_data("\r\n");
			}
		&reset_byte_count();
		while($line = <CGIOUTr>) {
			&write_data($line);
			}
		close(CGIOUTr);
		close(CGIERRr);
		unlink($infile) if ($infile);
		$rv = 0;
		}
	}
else {
	# A file to output
	print DEBUG "handle_request: outputting file\n";
	open(FILE, $full) || &http_error(404, "Failed to open file");
	binmode(FILE);
	&write_data("HTTP/1.0 $ok_code $ok_message\r\n");
	&write_data("Date: $datestr\r\n");
	&write_data("Server: $config{server}\r\n");
	&write_data("Content-type: ".&get_type($full)."\r\n");
	&write_data("Content-length: $stfull[7]\r\n");
	&write_data("Last-Modified: ".&http_date($stfull[9])."\r\n");
	$rv = &write_keep_alive();
	&write_data("\r\n");
	&reset_byte_count();
	while(read(FILE, $buf, 1024) > 0) {
		&write_data($buf);
		}
	close(FILE);
	}

# log the request
&log_request($acpthost, $authuser, $reqline,
	     $logged_code ? $logged_code :
	     $cgiheader{"location"} ? "302" : $ok_code, &byte_count());
return $rv;
}

# http_error(code, message, body, [dontexit])
sub http_error
{
local $eh = $error_handler_recurse ? undef :
	    $config{"error_handler_$_[0]"} ? $config{"error_handler_$_[0]"} :
	    $config{'error_handler'} ? $config{'error_handler'} : undef;
print DEBUG "http_error code=$_[0] message=$_[1] body=$_[2]\n";
if ($eh) {
	# Call a CGI program for the error
	$page = "/$eh";
	$querystring = "code=$_[0]&message=".&urlize($_[1]).
		       "&body=".&urlize($_[2]);
	$error_handler_recurse++;
	$ok_code = $_[0];
	$ok_message = $_[1];
	goto rerun;
	}
else {
	# Use the standard error message display
	&write_data("HTTP/1.0 $_[0] $_[1]\r\n");
	&write_data("Server: $config{server}\r\n");
	&write_data("Date: $datestr\r\n");
	&write_data("Content-type: text/html\r\n");
	&write_keep_alive(0);
	&write_data("\r\n");
	&reset_byte_count();
	&write_data("<h1>Error - $_[1]</h1>\n");
	if ($_[2]) {
		&write_data("<pre>$_[2]</pre>\n");
		}
	}
&log_request($acpthost, $authuser, $reqline, $_[0], &byte_count())
	if ($reqline);
&log_error($_[1], $_[2] ? " : $_[2]" : "");
shutdown(SOCK, 1);
exit if (!$_[3]);
}

sub get_type
{
if ($_[0] =~ /\.([A-z0-9]+)$/) {
	$t = $mime{$1};
	if ($t ne "") {
		return $t;
		}
	}
return "text/plain";
}

# simplify_path(path, bogus)
# Given a path, maybe containing stuff like ".." and "." convert it to a
# clean, absolute form.
sub simplify_path
{
local($dir, @bits, @fixedbits, $b);
$dir = $_[0];
$dir =~ s/\\/\//g;	# fix windows \ in path
$dir =~ s/^\/+//g;
$dir =~ s/\/+$//g;
$dir =~ s/\0//g;	# remove null bytes
@bits = split(/\/+/, $dir);
@fixedbits = ();
$_[1] = 0;
foreach $b (@bits) {
        if ($b eq ".") {
                # Do nothing..
                }
        elsif ($b eq ".." || $b eq "...") {
                # Remove last dir
                if (scalar(@fixedbits) == 0) {
                        $_[1] = 1;
                        return "/";
                        }
                pop(@fixedbits);
                }
        else {
                # Add dir to list
                push(@fixedbits, $b);
                }
        }
return "/" . join('/', @fixedbits);
}

# b64decode(string)
# Converts a string from base64 format to normal
sub b64decode
{
    local($str) = $_[0];
    local($res);
    $str =~ tr|A-Za-z0-9+=/||cd;
    $str =~ s/=+$//;
    $str =~ tr|A-Za-z0-9+/| -_|;
    while ($str =~ /(.{1,60})/gs) {
        my $len = chr(32 + length($1)*3/4);
        $res .= unpack("u", $len . $1 );
    }
    return $res;
}

# ip_match(remoteip, localip, [match]+)
# Checks an IP address against a list of IPs, networks and networks/masks
sub ip_match
{
local(@io, @mo, @ms, $i, $j, $hn, $needhn);
@io = split(/\./, $_[0]);
for($i=2; $i<@_; $i++) {
	$needhn++ if ($_[$i] =~ /^\*(\S+)$/);
	}
if ($needhn && !defined($hn = $ip_match_cache{$_[0]})) {
	$hn = gethostbyaddr(inet_aton($_[0]), AF_INET);
	$hn = "" if (&to_ipaddress($hn) ne $_[0]);
	$ip_match_cache{$_[0]} = $hn;
	}
for($i=2; $i<@_; $i++) {
	local $mismatch = 0;
	if ($_[$i] =~ /^(\S+)\/(\d+)$/) {
		# Convert CIDR to netmask format
		$_[$i] = $1."/".&prefix_to_mask($2);
		}
	if ($_[$i] =~ /^(\S+)\/(\S+)$/) {
		# Compare with network/mask
		@mo = split(/\./, $1); @ms = split(/\./, $2);
		for($j=0; $j<4; $j++) {
			if ((int($io[$j]) & int($ms[$j])) != int($mo[$j])) {
				$mismatch = 1;
				}
			}
		}
	elsif ($_[$i] =~ /^\*(\S+)$/) {
		# Compare with hostname regexp
		$mismatch = 1 if ($hn !~ /$1$/);
		}
	elsif ($_[$i] eq 'LOCAL') {
		# Compare with local network
		local @lo = split(/\./, $_[1]);
		if ($lo[0] < 128) {
			$mismatch = 1 if ($lo[0] != $io[0]);
			}
		elsif ($lo[0] < 192) {
			$mismatch = 1 if ($lo[0] != $io[0] ||
					  $lo[1] != $io[1]);
			}
		else {
			$mismatch = 1 if ($lo[0] != $io[0] ||
					  $lo[1] != $io[1] ||
					  $lo[2] != $io[2]);
			}
		}
	elsif ($_[$i] !~ /^[0-9\.]+$/) {
		# Compare with hostname
		$mismatch = 1 if ($_[0] ne &to_ipaddress($_[$i]));
		}
	else {
		# Compare with IP or network
		@mo = split(/\./, $_[$i]);
		while(@mo && !$mo[$#mo]) { pop(@mo); }
		for($j=0; $j<@mo; $j++) {
			if ($mo[$j] != $io[$j]) {
				$mismatch = 1;
				}
			}
		}
	return 1 if (!$mismatch);
	}
return 0;
}

# users_match(&uinfo, user, ...)
# Returns 1 if a user is in a list of users and groups
sub users_match
{
local $uinfo = shift(@_);
local $u;
local @ginfo = getgrgid($uinfo->[3]);
foreach $u (@_) {
	if ($u =~ /^\@(\S+)$/) {
		return 1 if (&is_group_member($uinfo, $1));
		}
	elsif ($u =~ /^(\d*)-(\d*)$/ && ($1 || $2)) {
		return (!$1 || $uinfo[2] >= $1) &&
		       (!$2 || $uinfo[2] <= $2);
		}
	else {
		return 1 if ($u eq $uinfo->[0]);
		}
	}
return 0;
}

# restart_miniserv()
# Called when a SIGHUP is received to restart the web server. This is done
# by exec()ing perl with the same command line as was originally used
sub restart_miniserv
{
print STDERR "restarting miniserv\n";
&log_error("Restarting");
close(SOCK);
&close_all_sockets();
&close_all_pipes();
kill('KILL', $logclearer) if ($logclearer);
kill('KILL', $extauth) if ($extauth);
exec($perl_path, $miniserv_path, @miniserv_argv);
die "Failed to restart miniserv with $perl_path $miniserv_path";
}

sub trigger_restart
{
$need_restart = 1;
}

sub trigger_reload
{
$need_reload = 1;
}

sub to_ipaddress
{
local (@rv, $i);
foreach $i (@_) {
	if ($i =~ /(\S+)\/(\S+)/ || $i =~ /^\*\S+$/ ||
	    $i eq 'LOCAL' || $i =~ /^[0-9\.]+$/) { push(@rv, $i); }
	else { push(@rv, join('.', unpack("CCCC", inet_aton($i)))); }
	}
return wantarray ? @rv : $rv[0];
}

# read_line(no-wait, no-limit)
# Reads one line from SOCK or SSL
sub read_line
{
local ($nowait, $nolimit) = @_;
local($idx, $more, $rv);
while(($idx = index($main::read_buffer, "\n")) < 0) {
	if (length($main::read_buffer) > 10000 && !$nolimit) {
		&http_error(414, "Request too long",
		    "Received excessive line <pre>$main::read_buffer</pre>");
		}

	# need to read more..
	&wait_for_data_error() if (!$nowait);
	if ($use_ssl) {
		$more = Net::SSLeay::read($ssl_con);
		}
	else {
                local $ok = sysread(SOCK, $more, 1024);
		$more = undef if ($ok <= 0);
		}
	if ($more eq '') {
		# end of the data
		$rv = $main::read_buffer;
		undef($main::read_buffer);
		return $rv;
		}
	$main::read_buffer .= $more;
	}
$rv = substr($main::read_buffer, 0, $idx+1);
$main::read_buffer = substr($main::read_buffer, $idx+1);
return $rv;
}

# read_data(length)
# Reads up to some amount of data from SOCK or the SSL connection
sub read_data
{
local ($rv);
if (length($main::read_buffer)) {
	if (length($main::read_buffer) > $_[0]) {
		# Return the first part of the buffer
		$rv = substr($main::read_buffer, 0, $_[0]);
		$main::read_buffer = substr($main::read_buffer, $_[0]);
		return $rv;
		}
	else {
		# Return the whole buffer
		$rv = $main::read_buffer;
		undef($main::read_buffer);
		return $rv;
		}
	}
elsif ($use_ssl) {
	# Call SSL read function
	return Net::SSLeay::read($ssl_con, $_[0]);
	}
else {
	# Just do a normal read
	local $buf;
	sysread(SOCK, $buf, $_[0]) || return undef;
	return $buf;
	}
}

# sysread_line(fh)
# Read a line from a file handle, using sysread to get a byte at a time
sub sysread_line
{
local ($fh) = @_;
local $line;
while(1) {
	local ($buf, $got);
	$got = sysread($fh, $buf, 1);
	last if ($got <= 0);
	$line .= $buf;
	last if ($buf eq "\n");
	}
return $line;
}

# wait_for_data(secs)
# Waits at most the given amount of time for some data on SOCK, returning
# 0 if not found, 1 if some arrived.
sub wait_for_data
{
local $rmask;
vec($rmask, fileno(SOCK), 1) = 1;
local $got = select($rmask, undef, undef, $_[0]);
return $got == 0 ? 0 : 1;
}

# wait_for_data_error()
# Waits 60 seconds for data on SOCK, and fails if none arrives
sub wait_for_data_error
{
local $got = &wait_for_data(60);
if (!$got) {
	&http_error(400, "Timeout",
		    "Waited more than 60 seconds for request data");
	}
}

# write_data(data, ...)
# Writes a string to SOCK or the SSL connection
sub write_data
{
local $str = join("", @_);
if ($use_ssl) {
	Net::SSLeay::write($ssl_con, $str);
	}
else {
	syswrite(SOCK, $str, length($str));
	}
# Intentionally introduce a small delay to avoid problems where IE reports
# the page as empty / DNS failed when it get a large response too quickly!
select(undef, undef, undef, .01) if ($write_data_count%10 == 0);
$write_data_count += length($str);
}

# reset_byte_count()
sub reset_byte_count { $write_data_count = 0; }

# byte_count()
sub byte_count { return $write_data_count; }

# log_request(hostname, user, request, code, bytes)
sub log_request
{
if ($config{'log'}) {
	local ($user, $ident, $headers);
	if ($config{'logident'}) {
		# add support for rfc1413 identity checking here
		}
	else { $ident = "-"; }
	$user = $_[1] ? $_[1] : "-";
	local $dstr = &make_datestr();
	if (fileno(MINISERVLOG)) {
		seek(MINISERVLOG, 0, 2);
		}
	else {
		open(MINISERVLOG, ">>$config{'logfile'}");
		chmod(0600, $config{'logfile'});
		}
	if (defined($config{'logheaders'})) {
		foreach $h (split(/\s+/, $config{'logheaders'})) {
			$headers .= " $h=\"$header{$h}\"";
			}
		}
	elsif ($config{'logclf'}) {
		$headers = " \"$header{'referer'}\" \"$header{'user-agent'}\"";
		}
	else {
		$headers = "";
		}
	print MINISERVLOG "$_[0] $ident $user [$dstr] \"$_[2]\" ",
			  "$_[3] $_[4]$headers\n";
	close(MINISERVLOG);
	}
}

# make_datestr()
sub make_datestr
{
local @tm = localtime(time());
return sprintf "%2.2d/%s/%4.4d:%2.2d:%2.2d:%2.2d %s",
		$tm[3], $month[$tm[4]], $tm[5]+1900,
	        $tm[2], $tm[1], $tm[0], $timezone;
}

# log_error(message)
sub log_error
{
seek(STDERR, 0, 2);
print STDERR "[",&make_datestr(),"] ",
	$acpthost ? ( "[",$acpthost,"] " ) : ( ),
	$page ? ( $page," : " ) : ( ),
	@_,"\n";
}

# read_errors(handle)
# Read and return all input from some filehandle
sub read_errors
{
local($fh, $_, $rv);
$fh = $_[0];
while(<$fh>) { $rv .= $_; }
return $rv;
}

sub write_keep_alive
{
local $mode;
if ($config{'nokeepalive'}) {
	# Keep alives have been disabled in config
	$mode = 0;
	}
elsif (@childpids > $config{'maxconns'}*.8) {
	# Disable because nearing process limit
	$mode = 0;
	}
elsif (@_) {
	# Keep alive specified by caller
	$mode = $_[0];
	}
else {
	# Keep alive determined by browser
	$mode = $header{'connection'} =~ /keep-alive/i;
	}
&write_data("Connection: ".($mode ? "Keep-Alive" : "close")."\r\n");
return $mode;
}

sub term_handler
{
kill('TERM', @childpids) if (@childpids);
kill('KILL', $logclearer) if ($logclearer);
kill('KILL', $extauth) if ($extauth);
exit(1);
}

sub http_date
{
local @tm = gmtime($_[0]);
return sprintf "%s, %d %s %d %2.2d:%2.2d:%2.2d GMT",
		$weekday[$tm[6]], $tm[3], $month[$tm[4]], $tm[5]+1900,
		$tm[2], $tm[1], $tm[0];
}

sub TIEHANDLE
{
my $i; bless \$i, shift;
}
 
sub WRITE
{
$r = shift;
my($buf,$len,$offset) = @_;
&write_to_sock(substr($buf, $offset, $len));
}
 
sub PRINT
{
$r = shift;
$$r++;
my $buf = join(defined($,) ? $, : "", @_);
$buf .= $\ if defined($\);
&write_to_sock($buf);
}
 
sub PRINTF
{
shift;
my $fmt = shift;
&write_to_sock(sprintf $fmt, @_);
}
 
# Send back already read data while we have it, then read from SOCK
sub READ
{
my $r = shift;
my $bufref = \$_[0];
my $len = $_[1];
my $offset = $_[2];
if ($postpos < length($postinput)) {
	# Reading from already fetched array
	my $left = length($postinput) - $postpos;
	my $canread = $len > $left ? $left : $len;
	substr($$bufref, $offset, $canread) =
		substr($postinput, $postpos, $canread);
	$postpos += $canread;
	return $canread;
	}
else {
	# Read from network socket
	local $data = &read_data($len);
	if ($data eq '' && $len) {
		# End of socket
		print STDERR "finished reading - shutting down socket\n";
		shutdown(SOCK, 0);
		}
	substr($$bufref, $offset, length($data)) = $data;
	return length($data);
	}
}

sub OPEN
{
#print STDERR "open() called - should never happen!\n";
}
 
# Read a line of input
sub READLINE
{
my $r = shift;
if ($postpos < length($postinput) &&
    ($idx = index($postinput, "\n", $postpos)) >= 0) {
	# A line exists in the memory buffer .. use it
	my $line = substr($postinput, $postpos, $idx-$postpos+1);
	$postpos = $idx+1;
	return $line;
	}
else {
	# Need to read from the socket
	my $line;
	if ($postpos < length($postinput)) {
		# Start with in-memory data
		$line = substr($postinput, $postpos);
		$postpos = length($postinput);
		}
	my $nl = &read_line(0, 1);
	if ($nl eq '') {
		# End of socket
		print STDERR "finished reading - shutting down socket\n";
		shutdown(SOCK, 0);
		}
	$line .= $nl if (defined($nl));
	return $line;
	}
}
 
# Read one character of input
sub GETC
{
my $r = shift;
my $buf;
my $got = READ($r, \$buf, 1, 0);
return $got > 0 ? $buf : undef;
}

sub FILENO
{
return fileno(SOCK);
}
 
sub CLOSE { }
 
sub DESTROY { }

# write_to_sock(data, ...)
sub write_to_sock
{
local $d;
foreach $d (@_) {
	if ($doneheaders || $miniserv::nph_script) {
		&write_data($d);
		}
	else {
		$headers .= $d;
		while(!$doneheaders && $headers =~ s/^([^\r\n]*)(\r)?\n//) {
			if ($1 =~ /^(\S+):\s+(.*)$/) {
				$cgiheader{lc($1)} = $2;
				push(@cgiheader, [ $1, $2 ]);
				}
			elsif ($1 !~ /\S/) {
				$doneheaders++;
				}
			else {
				&http_error(500, "Bad Header");
				}
			}
		if ($doneheaders) {
			if ($cgiheader{"location"}) {
				&write_data(
					"HTTP/1.0 302 Moved Temporarily\r\n");
				&write_data("Date: $datestr\r\n");
				&write_data("Server: $config{server}\r\n");
				&write_keep_alive(0);
				}
			elsif ($cgiheader{"content-type"} eq "") {
				&http_error(500, "Missing Content-Type Header");
				}
			else {
				&write_data("HTTP/1.0 $ok_code $ok_message\r\n");
				&write_data("Date: $datestr\r\n");
				&write_data("Server: $config{server}\r\n");
				&write_keep_alive(0);
				}
			foreach $h (@cgiheader) {
				&write_data("$h->[0]: $h->[1]\r\n");
				}
			&write_data("\r\n");
			&reset_byte_count();
			&write_data($headers);
			}
		}
	}
}

sub verify_client
{
local $cert = Net::SSLeay::X509_STORE_CTX_get_current_cert($_[1]);
if ($cert) {
	local $errnum = Net::SSLeay::X509_STORE_CTX_get_error($_[1]);
	$verified_client = 1 if (!$errnum);
	}
return 1;
}

sub END
{
if ($doing_eval && $$ == $main_process_id) {
	# A CGI program called exit! This is a horrible hack to 
	# finish up before really exiting
	shutdown(SOCK, 1);
	close(SOCK);
	close($PASSINw); close($PASSOUTw);
	&log_request($acpthost, $authuser, $reqline,
		     $cgiheader{"location"} ? "302" : $ok_code, &byte_count());
	}
}

# urlize
# Convert a string to a form ok for putting in a URL
sub urlize {
  local($tmp, $tmp2, $c);
  $tmp = $_[0];
  $tmp2 = "";
  while(($c = chop($tmp)) ne "") {
	if ($c !~ /[A-z0-9]/) {
		$c = sprintf("%%%2.2X", ord($c));
		}
	$tmp2 = $c . $tmp2;
	}
  return $tmp2;
}

# validate_user(username, password, host)
# Checks if some username and password are valid. Returns the modified username,
# the expired flag, and the non-existence flag
sub validate_user
{
local ($user, $pass, $host) = @_;
return ( ) if (!$user);
print DEBUG "validate_user: user=$user pass=$pass host=$host\n";
local ($canuser, $canmode, $notexist, $webminuser, $sudo) =
	&can_user_login($user, undef, $host);
print DEBUG "validate_user: canuser=$canuser canmode=$canmode notexist=$notexist webminuser=$webminuser sudo=$sudo\n";
if ($notexist) {
	# User doesn't even exist, so go no further
	return ( undef, 0, 1 );
	}
elsif ($canmode == 0) {
	# User does exist but cannot login
	return ( $canuser, 0, 0 );
	}
elsif ($canmode == 1) {
	# Attempt Webmin authentication
	return $users{$webminuser} eq &unix_crypt($pass, $users{$webminuser}) ?
		( $user, 0, 0 ) : ( undef, 0, 0 );
	}
elsif ($canmode == 2 || $canmode == 3) {
	# Attempt PAM or passwd file authentication
	local $val = &validate_unix_user($canuser, $pass);
	print DEBUG "validate_user: unix val=$val\n";
	if ($val && $sudo) {
		# Need to check if this Unix user can sudo
		if (!&check_sudo_permissions($canuser, $pass)) {
			print DEBUG "validate_user: sudo failed\n";
			$val = 0;
			}
		else {
			print DEBUG "validate_user: sudo passed\n";
			}
		}
	return $val == 2 ? ( $canuser, 1, 0 ) :
	       $val == 1 ? ( $canuser, 0, 0 ) : ( undef, 0, 0 );
	}
elsif ($canmode == 4) {
	# Attempt external authentication
	return &validate_external_user($canuser, $pass) ?
		( $canuser, 0, 0 ) : ( undef, 0, 0 );
	}
else {
	# Can't happen!
	return ( );
	}
}

# validate_unix_user(user, password)
# Returns 1 if a username and password are valid under unix, 0 if not,
# or 2 if the account has expired.
# Checks PAM if available, and falls back to reading the system password
# file otherwise.
sub validate_unix_user
{
if ($use_pam) {
	# Check with PAM
	$pam_username = $_[0];
	$pam_password = $_[1];
	local $pamh = new Authen::PAM($config{'pam'}, $pam_username,
				      \&pam_conv_func);
	if (ref($pamh)) {
		local $pam_ret = $pamh->pam_authenticate();
		if ($pam_ret == PAM_SUCCESS()) {
			# Logged in OK .. make sure password hasn't expired
			local $acct_ret = $pamh->pam_acct_mgmt();
			if ($acct_ret == PAM_SUCCESS()) {
				$pamh->pam_open_session();
				return 1;
				}
			elsif ($acct_ret == PAM_NEW_AUTHTOK_REQD() ||
			       $acct_ret == PAM_ACCT_EXPIRED()) {
				return 2;
				}
			else {
				print STDERR "Unknown pam_acct_mgmt return value : $acct_ret\n";
				return 0;
				}
			}
		return 0;
		}
	}
elsif ($config{'pam_only'}) {
	# Pam is not available, but configuration forces it's use!
	return 0;
	}
elsif ($config{'passwd_file'}) {
	# Check in a password file
	local $rv = 0;
	open(FILE, $config{'passwd_file'});
	if ($config{'passwd_file'} eq '/etc/security/passwd') {
		# Assume in AIX format
		while(<FILE>) {
			s/\s*$//;
			if (/^\s*(\S+):/ && $1 eq $_[0]) {
				$_ = <FILE>;
				if (/^\s*password\s*=\s*(\S+)\s*$/) {
					$rv = $1 eq &unix_crypt($_[1], $1) ? 1 : 0;
					}
				last;
				}
			}
		}
	else {
		# Read the system password or shadow file
		while(<FILE>) {
			local @l = split(/:/, $_, -1);
			local $u = $l[$config{'passwd_uindex'}];
			local $p = $l[$config{'passwd_pindex'}];
			if ($u eq $_[0]) {
				$rv = $p eq &unix_crypt($_[1], $p) ? 1 : 0;
				if ($config{'passwd_cindex'} ne '' && $rv) {
					# Password may have expired!
					local $c = $l[$config{'passwd_cindex'}];
					local $m = $l[$config{'passwd_mindex'}];
					local $day = time()/(24*60*60);
					if ($c =~ /^\d+/ && $m =~ /^\d+/ &&
					    $day - $c > $m) {
						# Yep, it has ..
						$rv = 2;
						}
					}
				if ($p eq "" && $config{'passwd_blank'}) {
					# Force password change
					$rv = 2;
					}
				last;
				}
			}
		}
	close(FILE);
	return $rv if ($rv);
	}

# Fallback option - check password returned by getpw*
local @uinfo = getpwnam($_[0]);
if ($uinfo[1] ne '' && &unix_crypt($_[1], $uinfo[1]) eq $uinfo[1]) {
	return 1;
	}

return 0;	# Totally failed
}

# validate_external_user(user, pass)
# Validate a user by passing the username and password to an external
# squid-style authentication program
sub validate_external_user
{
return 0 if (!$config{'extauth'});
flock(EXTAUTH, 2);
local $str = "$_[0] $_[1]\n";
syswrite(EXTAUTH, $str, length($str));
local $resp = <EXTAUTH>;
flock(EXTAUTH, 8);
return $resp =~ /^OK/i ? 1 : 0;
}

# can_user_login(username, no-append, host)
# Checks if a user can login or not.
# First return value is the username.
# Second is 0 if cannot login, 1 if using Webmin pass, 2 if PAM, 3 if password
# file, 4 if external.
# Third is 1 if the user does not exist at all, 0 if he does.
# Fourth is the Webmin username whose permissions apply, based on unixauth.
# Fifth is a flag indicating if a sudo check is needed.
sub can_user_login
{
if (!$users{$_[0]}) {
	# See if this user exists in Unix and can be validated by the same
	# method as the unixauth webmin user
	local $realuser = $unixauth{$_[0]};
	local @uinfo;
	local $sudo = 0;
	local $pamany = 0;
	eval { @uinfo = getpwnam($_[0]); };	# may fail on windows
	if (!$realuser && @uinfo) {
		# No unixauth entry for the username .. try his groups 
		foreach my $ua (keys %unixauth) {
			if ($ua =~ /^\@(.*)$/) {
				if (&is_group_member(\@uinfo, $1)) {
					$realuser = $unixauth{$ua};
					last;
					}
				}
			}
		}
	if (!$realuser && @uinfo) {
		# Fall back to unix auth for all Unix users
		$realuser = $unixauth{"*"};
		}
	if (!$realuser && $use_sudo && @uinfo) {
		# Allow login effectively as root, if sudo permits it
		$sudo = 1;
		$realuser = "root";
		}
	if (!$realuser && !@uinfo && $config{'pamany'}) {
		# If the user completely doesn't exist, we can still allow
		# him to authenticate via PAM
		$realuser = $config{'pamany'};
		$pamany = 1;
		}
	if (!$realuser) {
		# For Usermin, always fall back to unix auth for any user,
		# so that later checks with domain added / removed are done.
		$realuser = $unixauth{"*"};
		}
	return (undef, 0, 1, undef) if (!$realuser);
	local $up = $users{$realuser};
	return (undef, 0, 1, undef) if (!defined($up));

	# Work out possible domain names from the hostname
	local @doms = ( $_[2] );
	if ($_[2] =~ /^([^\.]+)\.(\S+)$/) {
		push(@doms, $2);
		}

	if ($config{'user_mapping'} && !defined(%user_mapping)) {
		# Read the user mapping file
		%user_mapping = ();
		open(MAPPING, $config{'user_mapping'});
		while(<MAPPING>) {
			s/\r|\n//g;
			s/#.*$//;
			if (/^(\S+)\s+(\S+)/) {
				if ($config{'user_mapping_reverse'}) {
					$user_mapping{$1} = $2;
					}
				else {
					$user_mapping{$2} = $1;
					}
				}
			}
		close(MAPPING);
		}

	# Check the user mapping file to see if there is an entry for the
	# user login in which specifies a new effective user
	local $um;
	foreach my $d (@doms) {
		$um ||= $user_mapping{"$_[0]\@$d"};
		}
	$um ||= $user_mapping{$_[0]};
	if (defined($um) && ($_[1]&4) == 0) {
		# A mapping exists - use it!
		return &can_user_login($um, $_[1]+4, $_[2]);
		}

	# Check if a user with the entered login and the domains appended
	# or prepended exists, and if so take it to be the effective user
	if (!@uinfo && $config{'domainuser'}) {
		# Try again with name.domain and name.firstpart
		local @firsts = map { /^([^\.]+)/; $1 } @doms;
		if (($_[1]&1) == 0) {
			local ($a, $p);
			foreach $a (@firsts, @doms) {
				foreach $p ("$_[0].${a}", "$_[0]-${a}",
					    "${a}.$_[0]", "${a}-$_[0]",
					    "$_[0]_${a}", "${a}_$_[0]") {
					local @vu = &can_user_login(
							$p, $_[1]+1, $_[2]);
					return @vu if ($vu[1]);
					}
				}
			}
		}

	# Check if the user entered a domain at the end of his username when
	# he really shouldn't have, and if so try without it
	if (!@uinfo && $config{'domainstrip'} &&
	    $_[0] =~ /^(\S+)\@(\S+)$/ && ($_[1]&2) == 0) {
		local ($stripped, $dom) = ($1, $2);
		local @vu = &can_user_login($stripped, $_[1] + 2, $_[2]);
		return @vu if ($vu[1]);
		local @vu = &can_user_login($stripped, $_[1] + 2, $dom);
		return @vu if ($vu[1]);
		}

	return ( undef, 0, 1, undef ) if (!@uinfo && !$pamany);

	if (@uinfo) {
		if (defined(@allowusers)) {
			# Only allow people on the allow list
			return ( undef, 0, 0, undef )
				if (!&users_match(\@uinfo, @allowusers));
			}
		elsif (defined(@denyusers)) {
			# Disallow people on the deny list
			return ( undef, 0, 0, undef )
				if (&users_match(\@uinfo, @denyusers));
			}
		if ($config{'shells_deny'}) {
			local $found = 0;
			open(SHELLS, $config{'shells_deny'});
			while(<SHELLS>) {
				s/\r|\n//g;
				s/#.*$//;
				$found++ if ($_ eq $uinfo[8]);
				}
			close(SHELLS);
			return ( undef, 0, 0, undef ) if (!$found);
			}
		}

	if ($up eq 'x') {
		# PAM or passwd file authentication
		return ( $_[0], $use_pam ? 2 : 3, 0, $realuser, $sudo );
		}
	elsif ($up eq 'e') {
		# External authentication
		return ( $_[0], 4, 0, $realuser, $sudo );
		}
	else {
		# Fixed Webmin password
		return ( $_[0], 1, 0, $realuser, $sudo );
		}
	}
elsif ($users{$_[0]} eq 'x') {
	# Webmin user authenticated via PAM or password file
	return ( $_[0], $use_pam ? 2 : 3, 0, $_[0] );
	}
elsif ($users{$_[0]} eq 'e') {
	# Webmin user authenticated externally
	return ( $_[0], 4, 0, $_[0] );
	}
else {
	# Normal Webmin user
	return ( $_[0], 1, 0, $_[0] );
	}
}

# the PAM conversation function for interactive logins
sub pam_conv_func
{
$pam_conv_func_called++;
my @res;
while ( @_ ) {
	my $code = shift;
	my $msg = shift;
	my $ans = "";

	$ans = $pam_username if ($code == PAM_PROMPT_ECHO_ON() );
	$ans = $pam_password if ($code == PAM_PROMPT_ECHO_OFF() );

	push @res, PAM_SUCCESS();
	push @res, $ans;
	}
push @res, PAM_SUCCESS();
return @res;
}

sub urandom_timeout
{
close(RANDOM);
}

# get_socket_name(handle)
# Returns the local hostname or IP address of some connection
sub get_socket_name
{
return $config{'host'} if ($config{'host'});
local $sn = getsockname($_[0]);
return undef if (!$sn);
local $myaddr = (unpack_sockaddr_in($sn))[1];
if (!$get_socket_name_cache{$myaddr}) {
	local $myname;
	if (!$config{'no_resolv_myname'}) {
		$myname = gethostbyaddr($myaddr, AF_INET);
		}
	if ($myname eq "") {
		$myname = inet_ntoa($myaddr);
		}
	$get_socket_name_cache{$myaddr} = $myname;
	}
return $get_socket_name_cache{$myaddr};
}

# run_login_script(username, sid, remoteip, localip)
sub run_login_script
{
if ($config{'login_script'}) {
	system($config{'login_script'}.
	       " ".join(" ", map { quotemeta($_) } @_).
	       " >/dev/null 2>&1 </dev/null");
	}
}

# run_logout_script(username, sid, remoteip, localip)
sub run_logout_script
{
if ($config{'logout_script'}) {
	system($config{'logout_script'}.
	       " ".join(" ", map { quotemeta($_) } @_).
	       " >/dev/null 2>&1 </dev/null");
	}
}

# close_all_sockets()
# Closes all the main listening sockets
sub close_all_sockets
{
local $s;
foreach $s (@socketfhs) {
	close($s);
	}
}

# close_all_pipes()
# Close all pipes for talking to sub-processes
sub close_all_pipes
{
local $p;
foreach $p (@passin) { close($p); }
foreach $p (@passout) { close($p); }
foreach $p (values %conversations) {
	if ($p->{'PAMOUTr'}) {
		close($p->{'PAMOUTr'});
		close($p->{'PAMINw'});
		}
	}
}

# check_user_ip(user)
# Returns 1 if some user is allowed to login from the accepting IP, 0 if not
sub check_user_ip
{
if ($deny{$_[0]} &&
    &ip_match($acptip, $localip, @{$deny{$_[0]}}) ||
    $allow{$_[0]} &&
    !&ip_match($acptip, $localip, @{$allow{$_[0]}})) {
	return 0;
	}
return 1;
}

# check_user_time(user)
# Returns 1 if some user is allowed to login at the current date and time
sub check_user_time
{
return 1 if (!$allowdays{$_[0]} && !$allowhours{$_[0]});
local @tm = localtime(time());
if ($allowdays{$_[0]}) {
	# Make sure day is allowed
	return 0 if (&indexof($tm[6], @{$allowdays{$_[0]}}) < 0);
	}
if ($allowhours{$_[0]}) {
	# Make sure time is allowed
	local $m = $tm[2]*60+$tm[1];
	return 0 if ($m < $allowhours{$_[0]}->[0] ||
		     $m > $allowhours{$_[0]}->[1]);
	}
return 1;
}

# generate_random_id(password, [force-urandom])
# Returns a random session ID number
sub generate_random_id
{
local ($pass, $force_urandom) = @_;
local $sid;
if (!$bad_urandom) {
	# First try /dev/urandom, unless we have marked it as bad
	$SIG{ALRM} = "miniserv::urandom_timeout";
	alarm(5);
	if (open(RANDOM, "/dev/urandom")) {
		my $tmpsid;
		if (read(RANDOM, $tmpsid, 16) == 16) {
			$sid = lc(unpack('h*',$tmpsid));
			}
		close(RANDOM);
		}
	alarm(0);
	}
if (!$sid && !$force_urandom) {
	$sid = time();
	local $mul = 1;
	foreach $c (split(//, &unix_crypt($pass, substr($$, -2)))) {
		$sid += ord($c) * $mul;
		$mul *= 3;
		}
	}
return $sid;
}

# handle_login(username, ok, expired, not-exists, password)
# Called from handle_session to either mark a user as logged in, or not
sub handle_login
{
local ($vu, $ok, $expired, $nonexist, $pass) = @_;
$authuser = $vu if ($ok);

# check if the test cookie is set
if ($header{'cookie'} !~ /testing=1/ && $vu &&
    !$config{'no_testing_cookie'}) {
	&http_error(500, "No cookies",
	   "Your browser does not support cookies, ".
	   "which are required for this web server to ".
	   "work in session authentication mode");
	}

# check with main process for delay
if ($config{'passdelay'} && $vu) {
	print $PASSINw "delay $vu $acptip $ok\n";
	<$PASSOUTr> =~ /(\d+) (\d+)/;
	$blocked = $2;
	sleep($1);
	}

if ($ok && (!$expired ||
	    $config{'passwd_mode'} == 1)) {
	# Logged in OK! Tell the main process about
	# the new SID
	local $sid = &generate_random_id($pass);
	print $PASSINw "new $sid $authuser $acptip\n";

	# Run the post-login script, if any
	&run_login_script($authuser, $sid,
			  $acptip, $localip);

	# Check for a redirect URL for the user
	local $rurl = &login_redirect($authuser, $pass, $host);
	if ($rurl) {
		# Got one .. go to it
		&write_data("HTTP/1.0 302 Moved Temporarily\r\n");
		&write_data("Date: $datestr\r\n");
		&write_data("Server: $config{'server'}\r\n");
		&write_data("Location: $rurl\r\n");
		&write_keep_alive(0);
		&write_data("\r\n");
		&log_request($acpthost, $authuser, $reqline, 302, 0);
		}
	else {
		# Set cookie and redirect to originally requested page
		&write_data("HTTP/1.0 302 Moved Temporarily\r\n");
		&write_data("Date: $datestr\r\n");
		&write_data("Server: $config{'server'}\r\n");
		local $ssl = $use_ssl || $config{'inetd_ssl'};
		$portstr = $port == 80 && !$ssl ? "" :
			   $port == 443 && $ssl ? "" : ":$port";
		$prot = $ssl ? "https" : "http";
		local $sec = $ssl ? "; secure" : "";
		#$sec .= "; httpOnly";
		if ($in{'save'}) {
			&write_data("Set-Cookie: $sidname=$sid; path=/; expires=\"Fri, 1-Jan-2038 00:00:01\"$sec\r\n");
			}
		else {
			&write_data("Set-Cookie: $sidname=$sid; path=/$sec\r\n");
			}
		&write_data("Location: $prot://$host$portstr$in{'page'}\r\n");
		&write_keep_alive(0);
		&write_data("\r\n");
		&log_request($acpthost, $authuser, $reqline, 302, 0);
		syslog("info", "%s", "Successful login as $authuser from $acpthost") if ($use_syslog);
		&write_login_utmp($authuser, $acpthost);
		}
	return 0;
	}
elsif ($ok && $expired &&
       $config{'passwd_mode'} == 2) {
	# Login was ok, but password has expired. Need
	# to force display of password change form.
	$validated = 1;
	$authuser = undef;
	$querystring = "&user=".&urlize($vu).
		       "&pam=".$use_pam;
	$method = "GET";
	$queryargs = "";
	$page = $config{'password_form'};
	$logged_code = 401;
	$miniserv_internal = 2;
	syslog("crit", "%s",
		"Expired login as $vu ".
		"from $acpthost") if ($use_syslog);
	}
else {
	# Login failed, or password has expired. The login form will be
	# displayed again by later code
	$failed_user = $vu;
	$request_uri = $in{'page'};
	$already_session_id = undef;
	$method = "GET";
	$authuser = $baseauthuser = undef;
	syslog("crit", "%s",
		($nonexist ? "Non-existent" :
		 $expired ? "Expired" : "Invalid").
		" login as $vu from $acpthost")
		if ($use_syslog);
	}
return undef;
}

# write_login_utmp(user, host)
# Record the login by some user in utmp
sub write_login_utmp
{
if ($write_utmp) {
	# Write utmp record for login
	%utmp = ( 'ut_host' => $_[1],
		  'ut_time' => time(),
		  'ut_user' => $_[0],
		  'ut_type' => 7,	# user process
		  'ut_pid' => $main_process_id,
		  'ut_line' => $config{'pam'},
		  'ut_id' => '' );
	if (defined(&User::Utmp::putut)) {
		User::Utmp::putut(\%utmp);
		}
	else {
		User::Utmp::pututline(\%utmp);
		}
	}
}

# write_logout_utmp(user, host)
sub write_logout_utmp
{
if ($write_utmp) {
	# Write utmp record for logout
	%utmp = ( 'ut_host' => $_[1],
		  'ut_time' => time(),
		  'ut_user' => $_[0],
		  'ut_type' => 8,	# dead process
		  'ut_pid' => $main_process_id,
		  'ut_line' => $config{'pam'},
		  'ut_id' => '' );
	if (defined(&User::Utmp::putut)) {
		User::Utmp::putut(\%utmp);
		}
	else {
		User::Utmp::pututline(\%utmp);
		}
	}
}

# pam_conversation_process(username, write-pipe, read-pipe)
# This function is called inside a sub-process to communicate with PAM. It sends
# questions down one pipe, and reads responses from another
sub pam_conversation_process
{
local ($user, $writer, $reader) = @_;
$miniserv::pam_conversation_process_writer = $writer;
$miniserv::pam_conversation_process_reader = $reader;
local $convh = new Authen::PAM(
	$config{'pam'}, $user, \&miniserv::pam_conversation_process_func);
local $pam_ret = $convh->pam_authenticate();
if ($pam_ret == PAM_SUCCESS()) {
	local $acct_ret = $convh->pam_acct_mgmt();
	if ($acct_ret == PAM_SUCCESS()) {
		$convh->pam_open_session();
		print $writer "x2 $user 1 0 0\n";
		}
	elsif ($acct_ret == PAM_NEW_AUTHTOK_REQD() ||
	       $acct_ret == PAM_ACCT_EXPIRED()) {
		print $writer "x2 $user 1 1 0\n";
		}
	else {
		print $writer "x0 Unknown PAM account status $acct_ret\n";
		}
	}
else {
	print $writer "x2 $user 0 0 0\n";
	}
exit(0);
}

# pam_conversation_process_func(type, message, [type, message, ...])
# A pipe that talks to both PAM and the master process
sub pam_conversation_process_func
{
local @rv;
select($miniserv::pam_conversation_process_writer); $| = 1; select(STDOUT);
while(@_) {
	local ($type, $msg) = (shift, shift);
	$msg =~ s/\r|\n//g;
	local $ok = (print $miniserv::pam_conversation_process_writer "$type $msg\n");
	print $miniserv::pam_conversation_process_writer "\n";
	local $answer = <$miniserv::pam_conversation_process_reader>;
	$answer =~ s/\r|\n//g;
	push(@rv, PAM_SUCCESS(), $answer);
	}
push(@rv, PAM_SUCCESS());
return @rv;
}

# allocate_pipes()
# Returns 4 new pipe file handles
sub allocate_pipes
{
local ($PASSINr, $PASSINw, $PASSOUTr, $PASSOUTw);
local $p;
local %taken = ( (map { $_, 1 } @passin),
	         (map { $_->{'PASSINr'} } values %conversations) );
for($p=0; $taken{"PASSINr$p"}; $p++) { }
$PASSINr = "PASSINr$p";
$PASSINw = "PASSINw$p";
$PASSOUTr = "PASSOUTr$p";
$PASSOUTw = "PASSOUTw$p";
pipe($PASSINr, $PASSINw);
pipe($PASSOUTr, $PASSOUTw);
select($PASSINw); $| = 1;
select($PASSINr); $| = 1;
select($PASSOUTw); $| = 1;
select($PASSOUTw); $| = 1;
select(STDOUT);
return ($PASSINr, $PASSINw, $PASSOUTr, $PASSOUTw);
}

# recv_pam_question(&conv, fd)
# Reads one PAM question from the sub-process, and sends it to the HTTP handler.
# Returns 0 if the conversation is over, 1 if not.
sub recv_pam_question
{
local ($conf, $fh) = @_;
local $pr = $conf->{'PAMOUTr'};
select($pr); $| = 1; select(STDOUT);
local $line = <$pr>;
$line =~ s/\r|\n//g;
if (!$line) {
	$line = <$pr>;
	$line =~ s/\r|\n//g;
	}
$conf->{'last'} = time();
if (!$line) {
	# Failed!
	print $fh "0 PAM conversation error\n";
	return 0;
	}
else {
	local ($type, $msg) = split(/\s+/, $line, 2);
	if ($type =~ /^x(\d+)/) {
		# Pass this status code through
		print $fh "$1 $msg\n";
		return $1 == 2 || $1 == 0 ? 0 : 1;
		}
	elsif ($type == PAM_PROMPT_ECHO_ON()) {
		# A normal question
		print $fh "1 $msg\n";
		return 1;
		}
	elsif ($type == PAM_PROMPT_ECHO_OFF()) {
		# A password
		print $fh "3 $msg\n";
		return 1;
		}
	elsif ($type == PAM_ERROR_MSG() || $type == PAM_TEXT_INFO()) {
		# A message that does not require a response
		print $fh "4 $msg\n";
		return 1;
		}
	else {
		# Unknown type!
		print $fh "0 Unknown PAM message type $type\n";
		return 0;
		}
	}
}

# send_pam_answer(&conv, answer)
# Sends a response from the user to the PAM sub-process
sub send_pam_answer
{
local ($conf, $answer) = @_;
local $pw = $conf->{'PAMINw'};
$conf->{'last'} = time();
print $pw "$answer\n";
}

# end_pam_conversation(&conv)
# Clean up PAM conversation pipes and processes
sub end_pam_conversation
{
local ($conv) = @_;
kill('KILL', $conv->{'pid'}) if ($conv->{'pid'});
if ($conv->{'PAMINr'}) {
	close($conv->{'PAMINr'});
	close($conv->{'PAMOUTr'});
	close($conv->{'PAMINw'});
	close($conv->{'PAMOUTw'});
	}
delete($conversations{$conv->{'cid'}});
}

# get_ipkeys(&miniserv)
# Returns a list of IP address to key file mappings from a miniserv.conf entry
sub get_ipkeys
{
local (@rv, $k);
foreach $k (keys %{$_[0]}) {
	if ($k =~ /^ipkey_(\S+)/) {
		local $ipkey = { 'ips' => [ split(/,/, $1) ],
				 'key' => $_[0]->{$k},
				 'index' => scalar(@rv) };
		$ipkey->{'cert'} = $_[0]->{'ipcert_'.$1};
		push(@rv, $ipkey);
		}
	}
return @rv;
}

# create_ssl_context(keyfile, [certfile])
sub create_ssl_context
{
local ($keyfile, $certfile) = @_;
local $ssl_ctx;
eval { $ssl_ctx = Net::SSLeay::new_x_ctx() };
$ssl_ctx ||= Net::SSLeay::CTX_new();
$ssl_ctx || die "Failed to create SSL context : $!";
if ($client_certs) {
	Net::SSLeay::CTX_load_verify_locations(
		$ssl_ctx, $config{'ca'}, "");
	Net::SSLeay::CTX_set_verify(
		$ssl_ctx, &Net::SSLeay::VERIFY_PEER, \&verify_client);
	}
if ($config{'extracas'}) {
	local $p;
	foreach $p (split(/\s+/, $config{'extracas'})) {
		Net::SSLeay::CTX_load_verify_locations(
			$ssl_ctx, $p, "");
		}
	}

Net::SSLeay::CTX_use_RSAPrivateKey_file(
	$ssl_ctx, $keyfile,
	&Net::SSLeay::FILETYPE_PEM) || die "Failed to open SSL key $keyfile";
Net::SSLeay::CTX_use_certificate_file(
	$ssl_ctx, $certfile || $keyfile,
	&Net::SSLeay::FILETYPE_PEM) || die "Failed to open SSL cert $certfile";

return $ssl_ctx;
}

# ssl_connection_for_ip(socket)
# Returns a new SSL connection object for some socket, or undef if failed
sub ssl_connection_for_ip
{
local ($sock) = @_;
local $sn = getsockname($sock);
if (!$sn) {
	print STDERR "Failed to get address for socket $sock\n";
	return undef;
	}
local $myip = inet_ntoa((unpack_sockaddr_in($sn))[1]);
local $ssl_ctx = $ssl_contexts{$myip} || $ssl_contexts{"*"};
local $ssl_con = Net::SSLeay::new($ssl_ctx);
Net::SSLeay::set_fd($ssl_con, fileno($sock));
if (!Net::SSLeay::accept($ssl_con)) {
	print STDERR "Failed to initialize SSL connection\n";
	return undef;
	}
return $ssl_con;
}

# login_redirect(username, password, host)
# Calls the login redirect script (if configured), which may output a URL to
# re-direct a user to after logging in.
sub login_redirect
{
return undef if (!$config{'login_redirect'});
local $quser = quotemeta($_[0]);
local $qpass = quotemeta($_[1]);
local $qhost = quotemeta($_[2]);
local $url = `$config{'login_redirect'} $quser $qpass $qhost`;
chop($url);
return $url;
}

# reload_config_file()
# Re-read %config, and call post-config actions
sub reload_config_file
{
&log_error("Reloading configuration");
%config = &read_config_file($config_file);
&update_vital_config();
&read_users_file();
&read_mime_types();
&build_config_mappings();
if ($config{'session'}) {
	dbmclose(%sessiondb);
	dbmopen(%sessiondb, $config{'sessiondb'}, 0700);
	}
}

# read_config_file(file)
# Reads the given config file, and returns a hash of values
sub read_config_file
{
local %rv;
open(CONF, $_[0]) || die "Failed to open config file $_[0] : $!";
while(<CONF>) {
	s/\r|\n//g;
	if (/^#/ || !/\S/) { next; }
	/^([^=]+)=(.*)$/;
	$name = $1; $val = $2;
	$name =~ s/^\s+//g; $name =~ s/\s+$//g;
	$val =~ s/^\s+//g; $val =~ s/\s+$//g;
	$rv{$name} = $val;
	}
close(CONF);
return %rv;
}

# update_vital_config()
# Updates %config with defaults, and dies if something vital is missing
sub update_vital_config
{
my %vital = ("port", 80,
	  "root", "./",
	  "server", "MiniServ/0.01",
	  "index_docs", "index.html index.htm index.cgi index.php",
	  "addtype_html", "text/html",
	  "addtype_txt", "text/plain",
	  "addtype_gif", "image/gif",
	  "addtype_jpg", "image/jpeg",
	  "addtype_jpeg", "image/jpeg",
	  "realm", "MiniServ",
	  "session_login", "/session_login.cgi",
	  "pam_login", "/pam_login.cgi",
	  "password_form", "/password_form.cgi",
	  "password_change", "/password_change.cgi",
	  "maxconns", 50,
	  "pam", "webmin",
	  "sidname", "sid",
	  "unauth", "^/unauthenticated/ ^[A-Za-z0-9\\-/]+\\.jar\$ ^[A-Za-z0-9\\-/]+\\.class\$ ^[A-Za-z0-9\\-/]+\\.gif\$ ^[A-Za-z0-9\\-/]+\\.conf\$ ^[A-Za-z0-9\\-/]+\\.ico\$",
	  "max_post", 10000,
	 );
foreach my $v (keys %vital) {
	if (!$config{$v}) {
		if ($vital{$v} eq "") {
			die "Missing config option $v";
			}
		$config{$v} = $vital{$v};
		}
	}
if (!$config{'sessiondb'}) {
	$config{'pidfile'} =~ /^(.*)\/[^\/]+$/;
	$config{'sessiondb'} = "$1/sessiondb";
	}
if (!$config{'errorlog'}) {
	$config{'logfile'} =~ /^(.*)\/[^\/]+$/;
	$config{'errorlog'} = "$1/miniserv.error";
	}
if (!$config{'tempbase'}) {
	$config{'pidfile'} =~ /^(.*)\/[^\/]+$/;
	$config{'tempbase'} = "$1/cgitemp";
	}
if (!$config{'blockedfile'}) {
	$config{'pidfile'} =~ /^(.*)\/[^\/]+$/;
	$config{'blockedfile'} = "$1/blocked";
	}
}

# read_users_file()
# Fills the %users and %certs hashes from the users file in %config
sub read_users_file
{
undef(%users);
undef(%certs);
undef(%allow);
undef(%deny);
undef(%allowdays);
undef(%allowhours);
if ($config{'userfile'}) {
	open(USERS, $config{'userfile'});
	while(<USERS>) {
		s/\r|\n//g;
		local @user = split(/:/, $_, -1);
		$users{$user[0]} = $user[1];
		$certs{$user[0]} = $user[3] if ($user[3]);
		if ($user[4] =~ /^allow\s+(.*)/) {
			$allow{$user[0]} = $config{'alwaysresolve'} ?
				[ split(/\s+/, $1) ] :
				[ &to_ipaddress(split(/\s+/, $1)) ];
			}
		elsif ($user[4] =~ /^deny\s+(.*)/) {
			$deny{$user[0]} = $config{'alwaysresolve'} ?
				[ split(/\s+/, $1) ] :
				[ &to_ipaddress(split(/\s+/, $1)) ];
			}
		if ($user[5] =~ /days\s+(\S+)/) {
			$allowdays{$user[0]} = [ split(/,/, $1) ];
			}
		if ($user[5] =~ /hours\s+(\d+)\.(\d+)-(\d+).(\d+)/) {
			$allowhours{$user[0]} = [ $1*60+$2, $3*60+$4 ];
			}
		}
	close(USERS);
	}
}

# read_mime_types()
# Fills %mime with entries from file in %config and extra settings in %config
sub read_mime_types
{
undef(%mime);
if ($config{"mimetypes"} ne "") {
	open(MIME, $config{"mimetypes"});
	while(<MIME>) {
		chop; s/#.*$//;
		if (/^(\S+)\s+(.*)$/) {
			my $type = $1;
			my @exts = split(/\s+/, $2);
			foreach my $ext (@exts) {
				$mime{$ext} = $type;
				}
			}
		}
	close(MIME);
	}
foreach my $k (keys %config) {
	if ($k !~ /^addtype_(.*)$/) { next; }
	$mime{$1} = $config{$k};
	}
}

# build_config_mappings()
# Build the anonymous access list, IP access list, unauthenticated URLs list,
# redirect mapping and allow and deny lists from %config
sub build_config_mappings
{
# build anonymous access list
undef(%anonymous);
foreach my $a (split(/\s+/, $config{'anonymous'})) {
	if ($a =~ /^([^=]+)=(\S+)$/) {
		$anonymous{$1} = $2;
		}
	}

# build IP access list
undef(%ipaccess);
foreach my $a (split(/\s+/, $config{'ipaccess'})) {
	if ($a =~ /^([^=]+)=(\S+)$/) {
		$ipaccess{$1} = $2;
		}
	}

# build unauthenticated URLs list
@unauth = split(/\s+/, $config{'unauth'});

# build redirect mapping
undef(%redirect);
foreach my $r (split(/\s+/, $config{'redirect'})) {
	if ($r =~ /^([^=]+)=(\S+)$/) {
		$redirect{$1} = $2;
		}
	}

# build prefixes to be stripped
undef(@strip_prefix);
foreach my $r (split(/\s+/, $config{'strip_prefix'})) {
	push(@strip_prefix, $r);
	}

# Init allow and deny lists
@deny = split(/\s+/, $config{"deny"});
@deny = &to_ipaddress(@deny) if (!$config{'alwaysresolve'});
@allow = split(/\s+/, $config{"allow"});
@allow = &to_ipaddress(@allow) if (!$config{'alwaysresolve'});
undef(@allowusers);
undef(@denyusers);
if ($config{'allowusers'}) {
	@allowusers = split(/\s+/, $config{'allowusers'});
	}
elsif ($config{'denyusers'}) {
	@denyusers = split(/\s+/, $config{'denyusers'});
	}

# Build list of unixauth mappings
undef(%unixauth);
foreach my $ua (split(/\s+/, $config{'unixauth'})) {
	if ($ua =~ /^(\S+)=(\S+)$/) {
		$unixauth{$1} = $2;
		}
	else {
		$unixauth{"*"} = $ua;
		}
	}

# Build list of non-session-auth pages
undef(%sessiononly);
foreach my $sp (split(/\s+/, $config{'sessiononly'})) {
	$sessiononly{$sp} = 1;
	}

# Build list of logout times
undef(@logouttimes);
foreach my $a (split(/\s+/, $config{'logouttimes'})) {
	if ($a =~ /^([^=]+)=(\S+)$/) {
		push(@logouttimes, [ $1, $2 ]);
		}
	}
push(@logouttimes, [ undef, $config{'logouttime'} ]);

# Build list of DAV pathss
undef(@davpaths);
foreach my $d (split(/\s+/, $config{'davpaths'})) {
	push(@davpaths, $d);
	}
@davusers = split(/\s+/, $config{'dav_users'});

# Mobile agent substrings and hostname prefixes
@mobile_agents = split(/\t+/, $config{'mobile_agents'});
@mobile_prefixes = split(/\s+/, $config{'mobile_prefixes'});

# Open debug log
close(DEBUG);
if ($config{'debug'}) {
	open(DEBUG, ">>$config{'debug'}");
	}
else {
	open(DEBUG, ">/dev/null");
	}

# Reset cache of sudo checks
undef(%sudocache);
}

# is_group_member(&uinfo, groupname)
# Returns 1 if some user is a primary or secondary member of a group
sub is_group_member
{
local ($uinfo, $group) = @_;
local @ginfo = getgrnam($group);
return 0 if (!@ginfo);
return 1 if ($ginfo[2] == $uinfo->[3]);	# primary member
foreach my $m (split(/\s+/, $ginfo[3])) {
	return 1 if ($m eq $uinfo->[0]);
	}
return 0;
}

# prefix_to_mask(prefix)
# Converts a number like 24 to a mask like 255.255.255.0
sub prefix_to_mask
{
return $_[0] >= 24 ? "255.255.255.".(256-(2 ** (32-$_[0]))) :
       $_[0] >= 16 ? "255.255.".(256-(2 ** (24-$_[0]))).".0" :
       $_[0] >= 8 ? "255.".(256-(2 ** (16-$_[0]))).".0.0" :
                     (256-(2 ** (8-$_[0]))).".0.0.0";
}

# get_logout_time(user, session-id)
# Given a username, returns the idle time before he will be logged out
sub get_logout_time
{
local ($user, $sid) = @_;
if (!defined($logout_time_cache{$user,$sid})) {
	local $time;
	foreach my $l (@logouttimes) {
		if ($l->[0] =~ /^\@(.*)$/) {
			# Check group membership
			local @uinfo = getpwnam($user);
			if (@uinfo && &is_group_member(\@uinfo, $1)) {
				$time = $l->[1];
				}
			}
		elsif ($l->[0] =~ /^\//) {
			# Check file contents
			open(FILE, $l->[0]);
			while(<FILE>) {
				s/\r|\n//g;
				s/^\s*#.*$//;
				if ($user eq $_) {
					$time = $l->[1];
					last;
					}
				}
			close(FILE);
			}
		elsif (!$l->[0]) {
			# Always match
			$time = $l->[1];
			}
		else {
			# Check username
			if ($l->[0] eq $user) {
				$time = $l->[1];
				}
			}
		last if (defined($time));
		}
	$logout_time_cache{$user,$sid} = $time;
	}
return $logout_time_cache{$user,$sid};
}

sub unix_crypt
{
local ($pass, $salt) = @_;
if ($use_perl_crypt) {
	return Crypt::UnixCrypt::crypt($pass, $salt);
	}
else {
	return crypt($pass, $salt);
	}
}

# handle_dav_request(davpath)
# Pass a request on to the Net::DAV::Server module
sub handle_dav_request
{
local ($path) = @_;
eval "use Filesys::Virtual::Plain";
eval "use Net::DAV::Server";
eval "use HTTP::Request";
eval "use HTTP::Headers";

if ($Net::DAV::Server::VERSION eq '1.28' && $config{'dav_nolock'}) {
	delete $Net::DAV::Server::implemented{lock};
	delete $Net::DAV::Server::implemented{unlock};
	}

# Read in request data
if (!$posted_data) {
	local $clen = $header{"content-length"};
	while(length($posted_data) < $clen) {
		$buf = &read_data($clen - length($posted_data));
		if (!length($buf)) {
			&http_error(500, "Failed to read POST request");
			}
		chomp($posted_data);
		#$posted_data =~ s/\015$//mg;
		$posted_data .= $buf;
		}
	}

# For subsequent logging
open(MINISERVLOG, ">>$config{'logfile'}");

# Switch to user
local $root;
local @u = getpwnam($authuser);
if ($config{'dav_remoteuser'} && !$< && $validated) {
	if (@u) {
		if ($u[2] != 0) {
			$( = $u[3]; $) = "$u[3] $u[3]";
			($>, $<) = ($u[2], $u[2]);
			}
		if ($config{'dav_root'} eq '*') {
			$root = $u[7];
			}
		}
	else {
		&http_error(500, "Unix user $authuser does not exist");
		return 0;
		}
	}
$root ||= $config{'dav_root'};
$root ||= "/";

# Check if this user can use DAV
if (@davusers) {
	&users_match(\@u, @davusers) ||
		&http_error(500, "You are not allowed to access DAV");
	}

# Create DAV server
my $filesys = Filesys::Virtual::Plain->new({root_path => $root});
my $webdav = Net::DAV::Server->new();
$webdav->filesys($filesys);

# Make up a request object, and feed to DAV
local $ho = HTTP::Headers->new;
foreach my $h (keys %header) {
	next if (lc($h) eq "connection");
	$ho->header($h => $header{$h});
	}
if ($path ne "/") {
	$request_uri =~ s/^\Q$path\E//;
	$request_uri = "/" if ($request_uri eq "");
	}
my $request = HTTP::Request->new($method, $request_uri, $ho,
				 $posted_data);
if ($config{'dav_debug'}) {
	print STDERR "DAV request :\n";
	print STDERR "---------------------------------------------\n";
	print STDERR $request->as_string();
	print STDERR "---------------------------------------------\n";
	}
my $response = $webdav->run($request);

# Send back the reply
&write_data("HTTP/1.1 ",$response->code()," ",$response->message(),"\r\n");
local $content = $response->content();
if ($path ne "/") {
	$content =~ s|href>/(.+)<|href>$path/$1<|g;
	$content =~ s|href>/<|href>$path<|g;
	}
foreach my $h ($response->header_field_names) {
	next if (lc($h) eq "connection" || lc($h) eq "content-length");
	&write_data("$h: ",$response->header($h),"\r\n");
	}
&write_data("Content-length: ",length($content),"\r\n");
local $rv = &write_keep_alive(0);
&write_data("\r\n");
&write_data($content);

if ($config{'dav_debug'}) {
	print STDERR "DAV reply :\n";
	print STDERR "---------------------------------------------\n";
	print STDERR "HTTP/1.1 ",$response->code()," ",$response->message(),"\r\n";
	foreach my $h ($response->header_field_names) {
		next if (lc($h) eq "connection" || lc($h) eq "content-length");
		print STDERR "$h: ",$response->header($h),"\r\n";
		}
	print STDERR "Content-length: ",length($content),"\r\n";
	print STDERR "\r\n";
	print STDERR $content;
	print STDERR "---------------------------------------------\n";
	}

# Log it
&log_request($acpthost, $authuser, $reqline, $response->code(), 
	     length($response->content()));
}

# get_system_hostname()
# Returns the hostname of this system, for reporting to listeners
sub get_system_hostname
{
# On Windows, try computername environment variable
return $ENV{'computername'} if ($ENV{'computername'});
return $ENV{'COMPUTERNAME'} if ($ENV{'COMPUTERNAME'});

# If a specific command is set, use it first
if ($config{'hostname_command'}) {
	local $out = `($config{'hostname_command'}) 2>&1`;
	if (!$?) {
		$out =~ s/\r|\n//g;
		return $out;
		}
	}

# First try the hostname command
local $out = `hostname 2>&1`;
if (!$? && $out =~ /\S/) {
	$out =~ s/\r|\n//g;
	return $out;
	}

# Try the Sys::Hostname module
eval "use Sys::Hostname";
if (!$@) {
	local $rv = eval "hostname()";
	if (!$@ && $rv) {
		return $rv;
		}
	}

# Must use net name on Windows
local $out = `net name 2>&1`;
if ($out =~ /\-+\r?\n(\S+)/) {
	return $1;
	}

return undef;
}

# indexof(string, array)
# Returns the index of some value in an array, or -1
sub indexof {
  local($i);
  for($i=1; $i <= $#_; $i++) {
    if ($_[$i] eq $_[0]) { return $i - 1; }
  }
  return -1;
}


# has_command(command)
# Returns the full path if some command is in the path, undef if not
sub has_command
{
local($d);
if (!$_[0]) { return undef; }
if (exists($has_command_cache{$_[0]})) {
	return $has_command_cache{$_[0]};
	}
local $rv = undef;
if ($_[0] =~ /^\//) {
	$rv = -x $_[0] ? $_[0] : undef;
	}
else {
	local $sp = $on_windows ? ';' : ':';
	foreach $d (split($sp, $ENV{PATH})) {
		if (-x "$d/$_[0]") {
			$rv = "$d/$_[0]";
			last;
			}
		if ($on_windows) {
			foreach my $sfx (".exe", ".com", ".bat") {
				if (-r "$d/$_[0]".$sfx) {
					$rv = "$d/$_[0]".$sfx;
					last;
					}
				}
			}
		}
	}
$has_command_cache{$_[0]} = $rv;
return $rv;
}

# check_sudo_permissions(user, pass)
# Returns 1 if some user can run any command via sudo
sub check_sudo_permissions
{
local ($user, $pass) = @_;

# First try the pipes
if ($PASSINw) {
	print DEBUG "check_sudo_permissions: querying cache for $user\n";
	print $PASSINw "readsudo $user\n";
	local $can = <$PASSOUTr>;
	chop($can);
	print DEBUG "check_sudo_permissions: cache said $can\n";
	if ($can =~ /^\d+$/ && $can != 2) {
		return int($can);
		}
	}

local $ptyfh = new IO::Pty;
print DEBUG "check_sudo_permissions: ptyfh=$ptyfh\n";
if (!$ptyfh) {
	print STDERR "Failed to create new PTY with IO::Pty\n";
	return 0;
	}
local @uinfo = getpwnam($user);
if (!@uinfo) {
	print STDERR "Unix user $user does not exist for sudo\n";
	return 0;
	}

# Execute sudo in a sub-process, via a pty
local $ttyfh = $ptyfh->slave();
print DEBUG "check_sudo_permissions: ttyfh=$ttyfh\n";
local $tty = $ptyfh->ttyname();
print DEBUG "check_sudo_permissions: tty=$tty\n";
chown($uinfo[2], $uinfo[3], $tty);
pipe(SUDOr, SUDOw);
print DEBUG "check_sudo_permissions: about to fork..\n";
local $pid = fork();
print DEBUG "check_sudo_permissions: fork=$pid pid=$$\n";
if ($pid < 0) {
	print STDERR "fork for sudo failed : $!\n";
	return 0;
	}
if (!$pid) {
	setsid();
	$ptyfh->make_slave_controlling_terminal();
	close(STDIN); close(STDOUT); close(STDERR);
	untie(*STDIN); untie(*STDOUT); untie(*STDERR);
	close($PASSINw); close($PASSOUTr);
	$( = $uinfo[3]; $) = "$uinfo[3] $uinfo[3]";
	($>, $<) = ($uinfo[2], $uinfo[2]);

	close(SUDOw);
	close(SOCK);
	close(MAIN);
	open(STDIN, "<&SUDOr");
	open(STDOUT, ">$tty");
	open(STDERR, ">&STDOUT");
	close($ptyfh);
	exec("sudo -l -S");
	print "Exec failed : $!\n";
	exit 1;
	}
print DEBUG "check_sudo_permissions: pid=$pid\n";
close(SUDOr);
$ptyfh->close_slave();

# Send password, and get back response
local $oldfh = select(SUDOw);
$| = 1;
select($oldfh);
print DEBUG "check_sudo_permissions: about to send pass\n";
local $SIG{'PIPE'} = 'ignore';	# Sometimes sudo doesn't ask for a password
print SUDOw $pass,"\n";
print DEBUG "check_sudo_permissions: sent pass=$pass\n";
close(SUDOw);
local $out;
while(<$ptyfh>) {
	print DEBUG "check_sudo_permissions: got $_";
	$out .= $_;
	}
close($ptyfh);
kill('KILL', $pid);
waitpid($pid, 0);
local ($ok) = ($out =~ /\(ALL\)\s+ALL/ ? 1 : 0);

# Update cache
if ($PASSINw) {
	print $PASSINw "writesudo $user $ok\n";
	}

return $ok;
}

# is_mobile_useragent(agent)
# Returns 1 if some user agent looks like a cellphone or other mobile device,
# such as a treo.
sub is_mobile_useragent
{
local ($agent) = @_;
local @prefixes = ( 
    "UP.Link",    # Openwave
    "Nokia",      # All Nokias start with Nokia
    "MOT-",       # All Motorola phones start with MOT-
    "SAMSUNG",    # Samsung browsers
    "Samsung",    # Samsung browsers
    "SEC-",       # Samsung browsers
    "AU-MIC",     # Samsung browsers
    "AUDIOVOX",   # Audiovox
    "BlackBerry", # BlackBerry
    "hiptop",     # Danger hiptop Sidekick
    "SonyEricsson", # Sony Ericsson
    "Ericsson",     # Old Ericsson browsers , mostly WAP
    "Mitsu/1.1.A",  # Mitsubishi phones
    "Panasonic WAP", # Panasonic old WAP phones
    "DoCoMo",     # DoCoMo phones
    "Lynx",	  # Lynx text-mode linux browser
    "Links",	  # Another text-mode linux browser
    );
local @substrings = (
    "UP.Browser",         # Openwave
    "MobilePhone",        # NetFront
    "AU-MIC-A700",        # Samsung A700 Obigo browsers
    "Danger hiptop",      # Danger Sidekick hiptop
    "Windows CE",         # Windows CE Pocket PC
    "Blazer",             # Palm Treo Blazer
    "BlackBerry",         # BlackBerries can emulate other browsers, but
                          # they still keep this string in the UserAgent
    "SymbianOS",          # New Series60 browser has safari in it and
                          # SymbianOS is the only distinguishing string
    );
foreach my $p (@prefixes) {
	return 1 if ($agent =~ /^\Q$p\E/);
	}
foreach my $s (@substrings, @mobile_agents) {
	return 1 if ($agent =~ /\Q$s\E/);
	}
return 0;
}

# write_blocked_file()
# Writes out a text file of blocked hosts and users
sub write_blocked_file
{
open(BLOCKED, ">$config{'blockedfile'}");
foreach my $d (grep { $hostfail{$_} } @deny) {
	print BLOCKED "host $d $hostfail{$d} $blockhosttime{$d}\n";
	}
foreach my $d (grep { $userfail{$_} } @denyusers) {
	print BLOCKED "user $d $userfail{$d} $blockusertime{$d}\n";
	}
close(BLOCKED);
chmod(0700, $config{'blockedfile'});
}

