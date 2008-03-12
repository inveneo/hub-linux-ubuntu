

var lang = 'en';
var tooltips = new Object;

function show_tooltip(event){
	var f = $(ASTGUI.events.getTarget(event)) ;
  try{
	if( f.hasAttribute('tip') ){
		var s = f.getAttribute('tip').split(",");
		top._$('tooltip').innerHTML = tooltips[s[1]][s[0]][s[2]]; 
	}
  }catch(er){}
}

//	Tooltips for users.html in english
	tooltips['users']= new Object;
	tooltips['users'] .en = new Array;

	tooltips['users'] .en[0] = "<B>Extension:</B> The numbered extension, i.e. 1234, that will be associated with this particular User / Phone." ;  //Extension
	tooltips['users'] .en[1] = "<B>Name:</B> A character-based name for this user, i.e. \"Bob Jones\" " ;  //Name
	tooltips['users'] .en[2] = "<B>Password:</B> The password for the user's sip/iax account , Ex: \"12u3b6\" " ; //Password
	tooltips['users'] .en[3] = "<B>E-Mail:</B> The e-mail address for this user, i.e. \"bobjones@bobjones.null\"";  //E-mail
	tooltips['users'] .en[4] = "<B>Caller ID:</B> The Caller ID (CID) string used when this user calls another user or number, i.e. \"800-555-1234\" "; //Caller ID
	tooltips['users'] .en[5] = "<B>Analog Phone:</B> If this user is attached to an analog port on the system, please choose the port number here.";  //Analog Phone
	tooltips['users'] .en[6] = "<B>Calling Rule:</B> Please choose the Calling Rule plan for this user as defined under the \"Calling Rules\" option to the left."; //Calling Rules
	tooltips['users'] .en[7] = "Advanced User and Phone options."; //Advanced
	tooltips['users'] .en[8] = "<B>Voicemail:</B> Check this box if the user should have a voicemail account."; //Voicemail
	tooltips['users'] .en[9] = "<B>In Directory:</B> Check this option if the user is to be listed in the telephone directory."; //In Directory
	tooltips['users'] .en[10] = "<B>Session Initiation Protocol</B> Check this option if the User or Phone is using SIP or is a SIP device."; //SIP
	tooltips['users'] .en[11] = "<B>InterAsterisk eXchange Protocol:</B> Check this option if the User or Phone is using IAX or is an IAX device.";  //IAX
	tooltips['users'] .en[12] = "<B>Computer Telephony Integration:</B> Check this option if the user is allowed to connect client applications to the Asterisk server."; //CTI:
	tooltips['users'] .en[13] = "<B>Call Waiting:</B> Check this option if the User or Phone should have Call-Waiting capability."; //Call Waiting
	tooltips['users'] .en[14] = "<B>3-Way Calling:</B>Check this option if the User or Phone should have 3-Way Calling capability."; //3-Way Calling:
	tooltips['users'] .en[15] = "<B>Is Agent:</B> Check this option if this User or Phone is an Call Queue Member (Agent)"; //Is Agent:
	tooltips['users'] .en[16] = "<B>VM Password:</B> Voicemail Password for this user, Ex: \"1234\"."; //Voicemail Password
	tooltips['users'] .en[17] = "<B>Hints:</B> If checked the phone being called will be sent a \"hint\" to light up status lamps on SIP phones."; // Hint phone before being dialed.
	tooltips['users'] .en[18] = "<B>Agent Login Extension:</B> Extension to be dialed for the Agents to Login to the Specific Queue. <br> This is an extension that all the Agents can Call to Login to their specified Queues. ";
	tooltips['users'] .en[19] = "<B>Agent Callback Login Extension:</B> Extension to be dialed for the Agents to Login to the Queues they are apart of.<br> Same as Agent Login Extension, except you do not have to remain on the line. ";
	tooltips['users'] .en[20] = "<B>Agent Logout</B><BR><LI> To logout of <b>Agent Login</b> Hangup your phone. <LI>To Logout of <b>Agent Callback Login</b> Dial the same extension used to login, specify your extension and password when prompted, and hit # when asked for your callback extension. This will successfully log you out of all queues you are apart of.";
	tooltips['users'] .en[21] = "<B>Can Reinvite:</B> This option can be used to tell the Asterisk server whethere or not to issue a reinvite to the client. ";
	tooltips['users'] .en[22] = "<B>NAT:</B> Try this setting when Asterisk is on a public IP, communicating with devices hidden behind a NAT device (broadband router). If you have one-way audio problems, you usually have problems with your NAT configuration or your firewall's support of SIP+RTP ports.";
	tooltips['users'] .en[23] = "<B>DTMFMode:</B> Set default dtmfmode for sending DTMF. Default: rfc2833 <BR><B>Other options:</B><BR>info : SIP INFO messages<BR>inband : Inband audio (requires 64 kbit codec -alaw, ulaw)<BR>auto : Use rfc2833 if offered, inband otherwise";
	tooltips['users'] .en[24] = "<B>Codecs:</B> Click to select the codecs that asterisk has to offer, for the particular user.";
	tooltips['users'] .en[25] = "<B>Email Only:</B> Send Voicemail to email only, do not store in the mailbox.";
	tooltips['users'] .en[26] = "<B>Insecure:</B> Matching of IP for a peer without matching port, do not require authentication of invites.<br><br>Options are:<br><ul><li>Port</li><li>Invite</li><li>port,invite</li></ul>";
	tooltips['users'] .en[99] = "<B>Phone Serial:</B> Enter the serial number of a Polycom phone to enable phone provisioning." ;

// Tooltips for Conferencing (meetme)
	tooltips['meetme']= new Object;
	tooltips['meetme'] .en = new Array;

	tooltips['meetme'] .en[0] = "<B>Extension:</B> This is the number dialed to reach this Conference Bridge.";  //Extension:
	tooltips['meetme'] .en[1] = "<B>Personal Identification Number:</B> Defining this option, i.e. \"1234\" sets a code that must be entered in order to access the Conference Bridge."; // Personal Identification Number
	tooltips['meetme'] .en[2] = "<B>Administrator PIN Code:</B> Defining this option sets a PIN for Conference Administrators."; // Administrator PIN Code
	tooltips['meetme'] .en[3] = "<B>Play Hold Music for First Caller:</B> Checking this option causes Asterisk to play Hold Music to the first user in a conference, until another user has joined the same conference.";
	tooltips['meetme'] .en[4] = "<B>Enable Caller Menu:</B> Checking this option allows a user to access the Conference Bridge menu by pressing the * \"Asterisk\" key on their dialpad.";
	tooltips['meetme'] .en[5] = "<B>Announce Callers:</B> Checking this option announces, to all Bridge participants, the joining of any other participants.";
	tooltips['meetme'] .en[6] = "<B>Advanced:</B> Show/Hide Advanced Conference Bridge configuration options.";
	tooltips['meetme'] .en[7] = "<B>Room Override:</B> This option allows the entry of a secondary extension that may be used to access this Conference Bridge. This is useful in the event that one wants to set a separate extension, having different options, to access the same Bridge.";
	tooltips['meetme'] .en[8] = "<B>Quiet Mode:</B> Do not play enter/leave sounds";
	tooltips['meetme'] .en[9] = "<B>Wait for Market User:</B> If this option is set, then users joining the conference will not be able to speak to one-another until the marked user has joined the conference.";
	tooltips['meetme'] .en[10] = "<B>Set Marked User:</B> This option sets the person that enters the bridge using this extension as Marked.  This option works in conjunction with the obove \"Wait for marked user\" option.";
	tooltips['meetme'] .en[11] = "<B>Record Conference:</B> Record this conference in a WAV format. Default filename is meetme-conf-rec-${Conference Number}-${UNIQUEID}.";

// Tooltips for Voicemail
	tooltips['voicemail']= new Object;
	tooltips['voicemail'] .en = new Array;

	tooltips['voicemail'] .en[0] = "<B>Extension for checking Message:</B>This option, i.e. \"2345,\" defines the extension that Users call in order to access their voicemail accounts.";
	tooltips['voicemail'] .en[1] = "<B>Attach recording to e-mail:</B> This option defines whether or not voicemails are sent to the Users' e-mail addresses as attachments.";
	tooltips['voicemail'] .en[2] = "<B>Say Message Caller-ID:</B> If this option is enabled, the Caller ID of the party that left the message will be played back before the voicemail message begins playing back.";
	tooltips['voicemail'] .en[3] = "<B>Say Message Duration:</B> If this optino is set, the duration of the message will be played back before the voicemail message begins playing back.";
	tooltips['voicemail'] .en[4] = "<B>Send messages by e-mail only:</B> If this option is set, then voicemails will not be checkable using a Phone.  Messages will be sent via e-mail, only.";
	tooltips['voicemail'] .en[5] = "<B>Maximum messages per folder:</B> This select box sets the maximum number of messages that a user may have in any of their folders.";
	tooltips['voicemail'] .en[6] = "<B>Maximum Message Time:</B> This select box sets the maximum duration of a voicemail message. Message recording will not occur for times greater than this amount.";
	tooltips['voicemail'] .en[7] = "<B>Minimum message Time:</B> This select box sets the minimum duration of a voicemail message. Messages below this threshold will be automatically deleted.";
	tooltips['voicemail'] .en[8] = "<B>Advanced:</B> Show/Hide Advanced Voicemail configuration options.";
	tooltips['voicemail'] .en[9] = "<B>Dail 'O' for Operator:</B> Checking this option enables callers entering the voicemail application to dial '0' to back out of the application and be sent to a voicemenu or operator.<BR><BR><B>Note:</B>You have to configure an Operator Extension from the 'Options' panel.";
	tooltips['voicemail'] .en[10] = "<B>Attach Format:</B> This selection box controls the format in which messages are delivered by e-mail.";
	tooltips['voicemail'] .en[11] = "<B>Allow Users to Review:</B> Checking this option allows the caller leaving the voicemail the opportunity to review their recorded message before it is submitted as a voicemail message.";
	tooltips['voicemail'] .en[12] = "<B>Play Envelope:</B> Selecting this option causes Asterisk not to play introductions about each message when accessing them from the voicemail application.";
	tooltips['voicemail'] .en[13] = "<B> Max Greeting:</B> Defining this option sets a maximum time for a users's voicemail away message.";

// Tooltips for CallQueues (queues)
	tooltips['queues']= new Object;
	tooltips['queues'].en = new Array;

	tooltips['queues'].en[0] = "<B>Queue:</B> This option defines the numbered extension that may be dialed to reach this Queue.";
	tooltips['queues'].en[1] = "<B>Full Name:</B> This option defines a name for this Queue, i.e. \"Sales\"";
	tooltips['queues'].en[2] = "<B>Strategy:</B>This option sets the Ringing Strategy for this Queue.  The options are:<OL><LI>RingAll - Ring All available Agents until one answers. <LI>RoundRobin - Take turns ringing each available Agent <LI>LeastRecent - Ring the Agent which was least recently called <LI>FewestCalls - Ring the Agent with the fewest completed calls <LI>Random - Ring a Random Agent <LI>RRmemory - RoundRobin with Memory, Rembers where it left off in the last ring pass</OL>";
	tooltips['queues'].en[3] = "<B>Agents:</B> This selection shows all Users defined as Agents in their User conf.  Checking a User here makes them a member of the current Queue.";
	tooltips['queues'].en[4] = "<B>Advanced:</B> Advanced Queue Configuration Options";
	tooltips['queues'].en[5] = "<B>Timeout:</B> This option defines the time in seconds that an Agent's phone rings before the next Agent is rung, i.e. \"15\" ";
	tooltips['queues'].en[6] = "<B>Wrapup Time:</B> After a successful call, time in seconds that an Agent remains free before another call is sent to them. Default is 0, which is No Delay.";
	tooltips['queues'].en[7] = "<B>AutoFill</B> Defining this option causes the Queue, when multiple calls are in it at the same time, to push them to Agents simultaneously.  Thus, instead of completing one call to an Agent at a time, the Queue will complete as many calls simultaneously to the available Agents.";
	tooltips['queues'].en[8] = "<B> AutoPause:</B> Enabling this option pauses an Agent if they fail to answer a call.";
	tooltips['queues'].en[9] = "<B> MaxLen:</B> This option sets the maximum number of callers that may wait in a Queue. Default is 0, Unlimited.";
	tooltips['queues'].en[10] = "<B> JoinEmpty:</B> Defining this option allows callers to enter the Queue when no Agents are available. If this option is not defined, callers will not be able to enter Queues with no available agents.";
	tooltips['queues'].en[11] = "<B>LeaveWhenEmpty:</B> Defining this option forces all callers to exit the Queue if New Callers are also not able to Enter the Queue. This option should generally be set in concert with the JoinEmpty option.";
	tooltips['queues'].en[12] = "<B> Report Hold Time:</B> Enabling this option causes Asterisk to report, to the Agent, the hold time of the caller before the caller is connected to the Agent.";
	tooltips['queues'].en[13] = "<B> Music On Hold:</B> Select the 'Music on Hold' Class for this Queue";

// Tooltips for SIP_General (sip_general)
	tooltips['sip_general']= new Object;
	tooltips['sip_general'].en = new Array;

	tooltips['sip_general'].en[0] = "<B>Context:</B> Default context for incoming calls";
	tooltips['sip_general'].en[1] = "<B>Realm for digest authentication:</B> Realm for digest authentication.defaults to \'asterisk\'. If you set a system name in asterisk.conf, it defaults to that system name. Realms MUST be globally unique according to RFC 3261. Set this to your host name or domain name";
	tooltips['sip_general'].en[2] = "<B>UDP Port to bind to:</B> SIP standard port is 5060";
	tooltips['sip_general'].en[3] = "<B>IP address to bind to:</B> 0.0.0.0 binds to all";
	tooltips['sip_general'].en[4] = "<B>Domain:</B> Comma separated list of domains which Asterisk is responsible for";
	tooltips['sip_general'].en[5] = "<B>Allow guest calls:</B> Enable guest calls.";
	tooltips['sip_general'].en[6] = "<B>Overlap dialing support:</B> Enable dialing support";
	tooltips['sip_general'].en[7] = "<B>Allow Transfers:</B> Enable Transfers";
	tooltips['sip_general'].en[8] = "<B>Enable DNS SRV lookups (on outbound calls): </B> Enable DNS SRV lookups on calls";
	tooltips['sip_general'].en[9] = "<B>Pedantic:</B> Enable slow, pedantic checking of Call-ID:s, multiline SIP headers and URI-encoded headers";
	tooltips['sip_general'].en[10] = "<B> Type of Service:</B> ";
	tooltips['sip_general'].en[11] = "<B> TOS for Signalling packets:</B> Sets Type of Service for SIP packets";
	tooltips['sip_general'].en[12] = "<B>TOS for RTP audio packets:</B> Sets Type of Service for RTP audio packets";
	tooltips['sip_general'].en[13] = "<B>TOS for RTP video packets:</B> Sets Type of Service for RTP video packets";
	tooltips['sip_general'].en[14] = "<B> Max Registration/Subscription Time:</B> Maximum duration (in seconds) of incoming registration/subscriptions we allow. Default 3600 seconds.";
	tooltips['sip_general'].en[15] = "<B> Min Registration/Subscription Time:</B> Minimum duration (in seconds) of registrations/subscriptions.  Default 60 seconds";
	tooltips['sip_general'].en[16] = "<B> Default Incoming/Outgoing Registration Time:</B>  Default duration (in seconds)  of incoming/outoing registration";
	tooltips['sip_general'].en[17] = "<B> Min RoundtripTime (T1 Time):</B>  Minimum roundtrip time for messages to monitored hosts,  Defaults to 100 ms";
	tooltips['sip_general'].en[18] = "<B> Override Notify MIME Type:</B> Allow overriding of mime type in MWI NOTIFY";
	tooltips['sip_general'].en[19] = "<B> Time between MWI Checks: </B> Default Time between Mailbox checks for peers";
	tooltips['sip_general'].en[20] = "<B> Music On Hold Interpret:</B> This option specifies a preference for which music on hold class this channel should listen to when put on hold if the music class has not been set on the channel with Set(CHANNEL(musicclass)=whatever) in the dialplan, and the peer channel putting this one on hold did not suggest a music class";
	tooltips['sip_general'].en[21] = "<B> Music On Hold Suggest:</B> This option specifies which music on hold class to suggest to the peer channel when this channel places the peer on hold. It may be specified globally or on a per-user or per-peer basis.";
	tooltips['sip_general'].en[22] = "<B> Language:</B> Default language setting for all users/peers";
	tooltips['sip_general'].en[23] = "<B> Enable Relaxed DTMF:</B> Relax dtmf handling";
	tooltips['sip_general'].en[24] = "<B> RTP TimeOut:</B> Terminate call if 60 seconds of no RTP activity when we're not on hold ";
	tooltips['sip_general'].en[25] = "<B>RTP HoldTimeOut:</B> Terminate call if 300 seconds of no RTP activity when we're on hold (must be > rtptimeout)";
	tooltips['sip_general'].en[26] = "<B>Trust Remote Party ID:</B> If Remote-Party-ID should be trusted";
	tooltips['sip_general'].en[27] = "<B>Send Remote Party ID:</B>If Remote-Party-ID should be sent";
	tooltips['sip_general'].en[28] = "<B>Generate In-Band Ringing:</B> If we should generate in-band ringing always use \'never\' to never use in-band signalling, even in cases where some buggy devices might not render it. Default: never";
	tooltips['sip_general'].en[29] = "<B>Server UserAgent:</B> Allows you to change the user agent string";
	tooltips['sip_general'].en[30] = "<B>Allow Nonlocal Redirect:</B>If checked, allows 302 or REDIR to non-local SIP address Note that promiscredir when redirects are made to the local system will cause loops since Asterisk is incapable of performing a \'hairpin\' call";
	tooltips['sip_general'].en[31] = "<B>Add 'user=phone' to URI:</B> If checked, \'user=phone\' is added to uri that contains a valid phone number";
	tooltips['sip_general'].en[32] = "<B>DTMF Mode:</B> Set default dtmfmode for sending DTMF. Default: rfc2833H";
	tooltips['sip_general'].en[33] = "<B>Send Compact SIP Headers:</B>  send compact sip headers";
	tooltips['sip_general'].en[34] = "<B> SIP Video Related:</B>";
	tooltips['sip_general'].en[35] = "<B>Max Bitrate (kb/s):</B>Maximum bitrate for video calls (default 384 kb/s)";
	tooltips['sip_general'].en[36] = "<B>Support for SIP Video:</B>Turn on support for SIP video";
	tooltips['sip_general'].en[37] = "<B>Generate Manager Events:</B> Generate manager events when sip ua performs events (e.g. hold)";
	tooltips['sip_general'].en[38] = "<B>Reject NonMatching Invites:</B> When an incoming INVITE or REGISTER is to be rejected, for any reason, always reject with \'401 Unauthorized\' instead of letting the requester know whether there was a matching user or peer for their request";
	tooltips['sip_general'].en[39] = "<B>NonStandard G.726 Support:</B>  If the peer negotiates G726-32 audio, use AAL2 packing order instead of RFC3551 packing order (this is required for Sipura and Grandstream ATAs, among others). This is contrary to the RFC3551 specification, the peer _should_ be negotiating AAL2-G726-32 instead";
	tooltips['sip_general'].en[40] = "<B> T.38 FAX Passthrough Support:</B>";
	tooltips['sip_general'].en[41] = "<B>T.38 fax (UDPTL) Passthrough:</B>Enables T.38 fax (UDPTL) passthrough on SIP to SIP calls";
	tooltips['sip_general'].en[42] = "<B>Sip Debugging:</B>";
	tooltips['sip_general'].en[43] = "<B>Enable SIP debugging: </B>Turn on SIP debugging by default ";
	tooltips['sip_general'].en[44] = "<B>Record SIP History:</B> Record SIP history by default";
	tooltips['sip_general'].en[45] = "<B>Dump SIP History:</B> Dump SIP history at end of SIP dialogue";
	tooltips['sip_general'].en[46] = "<B>Status Notifications (Subscriptions):</B>";
	tooltips['sip_general'].en[47] = "<B>Subscribe Context:</B>  Set a specific context for SUBSCRIBE requests. Useful to limit subscriptions to local extensions";
	tooltips['sip_general'].en[48] = "<B>Allow Subscribe:</B> Support for subscriptions.";
	tooltips['sip_general'].en[49] = "<B>Notify on Ringing:</B> Notify subscriptions on RINGING state";
	tooltips['sip_general'].en[50] = "<B>Outbound SIP Registrations:</B>";
	tooltips['sip_general'].en[51] = "<B>Register:</B> Register as a SIP user agent to a SIP proxy (provider)";
	tooltips['sip_general'].en[52] = "<B>Register TimeOut:</B> Retry registration calls at every \'x\' seconds (default 20)";
	tooltips['sip_general'].en[53] = "<B>Register Attempts:</B> Number of registration attempts before we give up; 0 = continue foreverp";
	tooltips['sip_general'].en[54] = "<B>NAT Support:</B>";
	tooltips['sip_general'].en[55] = "<B>Extern ip:</B>Address that we're going to put in outbound SIP messages if we're behind a NAT";
	tooltips['sip_general'].en[56] = "<B>Extern Host:</B>Alternatively you can specify an external host, and Asterisk will perform DNS queries periodically.  Not recommended for production environments!  Use externip instead";
	tooltips['sip_general'].en[57] = "<B>Extern Refresh:</B> How often to refresh externhost if used. You may specify a local network in the field below";
	tooltips['sip_general'].en[58] = "<B>Local Network Address: </B>  \'192.168.0.0/255.255.0.0\'  : All RFC 1918 addresses are local networks, \'10.0.0.0/255.0.0.0\' : Also RFC1918,  \'172.16.0.0/12\' : Another RFC1918 with CIDR notation, \'169.254.0.0/255.255.0.0\' : Zero conf local network";
	tooltips['sip_general'].en[59] = "<B>NAT mode:</B>Global NAT settings  (Affects all peers and users); yes = Always ignore info and assume NAT; no = Use NAT mode only according to RFC3581; never = Never attempt NAT mode or RFC3581 support; route = Assume NAT, don't send rport";
	tooltips['sip_general'].en[60] = "<B>Allow RTP Reinvite:</B>Asterisk by default tries to redirect the RTP media stream (audio) to go directly from the caller to the callee.  Some devices do not support this (especially if one of them is behind a NAT).";
	tooltips['sip_general'].en[61] = "<B>Realtime Support:</B>";
	tooltips['sip_general'].en[62] = "<B>Auto-Expire Friends:</B> Auto-Expire friends created on the fly on the same schedule as if it had just registered? (yes|no|<seconds>) If set to yes, when the registration expires, the friend will vanish from the configuration until requested again. If set to an integer, friends expire within this number of seconds instead of the registration interval.";
	tooltips['sip_general'].en[63] = "<B>Cache Friends: </B> Cache realtime friends by adding them to the internal list ";
	tooltips['sip_general'].en[64] = "<B>Save SysName:</B> Save systemname in realtime database at registration";
	tooltips['sip_general'].en[65] = "<B>Send Registry Updates:</B> Send registry updates to database using realtime?";
	tooltips['sip_general'].en[66] = "<B>Ignore Expired Peers:</B>  Enabling this setting has two functions: <P> For non-realtime peers, when their registration expires, the information will _not_ be removed from memory or the Asterisk database if you attempt to place a call to the peer, the existing information will be used in spiteof it having expired</P> <P>For realtime peers, when the peer is retrieved from realtime storage, the registration information will be used regardless of whether it has expired or not; if it expires while the realtime peer is still in memory (due to caching or other reasons), the information will not be removed from realtime storage</P>";
	tooltips['sip_general'].en[67] = "<B>SIP Domain Support:</B>";
	tooltips['sip_general'].en[68] = "<B>Domain:</B> List of \'allowed\' domains";
	tooltips['sip_general'].en[69] = "<B>From Domain:</B> When making outbound SIP INVITEs to non-peers, use your primary domain \'identity\' for From: headers instead of just your IP address. This is to be polite and it may be a mandatory requirement for some destinations which do not have a prior account relationship with your server. ";
	tooltips['sip_general'].en[70] = "<B>Auto Domain:</B>Turn this on to have Asterisk add local host name and local IP to domain list.";
	tooltips['sip_general'].en[71] = "<B>Allow External Domains:</B>Allow requests for domains not serviced by this server ";
	tooltips['sip_general'].en[72] = "<B>Allow External Invites:</B> Enable INVITE and REFER to non-local domains ";
	tooltips['sip_general'].en[73] = "<B> Jitter Buffer Configuration:</B> ";
	tooltips['sip_general'].en[74] = "<B>Enable Jitter Buffer:</B>  Enables the use of a jitterbuffer on the receiving side of a SIP channel.";
	tooltips['sip_general'].en[75] = "<B>Force Jitter Buffer:</B>Forces the use of a jitterbuffer on the receive side of a SIP channel ";
	tooltips['sip_general'].en[76] = "<B>Log Frames:</B>Enables jitterbuffer frame logging.";
	tooltips['sip_general'].en[77] = "<B>Max Jitter Buffer:</B> Max length of the jitterbuffer in milliseconds";
	tooltips['sip_general'].en[78] = "<B>Resync Threshold:</B> Jump in the frame timestamps over which the jitterbuffer is resynchronized. Useful to improve the quality of the voice, with big jumps in/broken timestamps, usualy sent from exotic devices and programs. Defaults to 1000.";
	tooltips['sip_general'].en[79] = "<B>Implementation: </B>Jitterbuffer implementation, used on the receiving side of a SIP channel. Two implementations are currenlty available - \'fixed\' (with size always equals to jbmaxsize) and \'adaptive\' (with variable size, actually the new jb of IAX2)";


// Tooltips for IAX_General (iax_general)
	tooltips['iax_general']= new Object;
	tooltips['iax_general'].en = new Array;
	tooltips['iax_general'].en[0] = "<B>Bind Port:</B> ";
	tooltips['iax_general'].en[1] = "<B>Bind Address:</B> ";
	tooltips['iax_general'].en[2] = "<B>IAX1 Compatibility:</B> ";
	tooltips['iax_general'].en[3] = "<B>No Checksums:</B> ";
	tooltips['iax_general'].en[4] = "<B>Delay Reject:</B> ";
	tooltips['iax_general'].en[5] = "<B>ADSI</B> ";
	tooltips['iax_general'].en[6] = "<B>AMA Flags:</B> ";
	tooltips['iax_general'].en[7] = "<B>Accountcode:</B> ";
	tooltips['iax_general'].en[8] = "<B>Music On Hold Interpret:</B> ";
	tooltips['iax_general'].en[9] = "<B>Music On Hold Suggest:</B> ";
	tooltips['iax_general'].en[10] = "<B>Language:</B> ";
	tooltips['iax_general'].en[11] = "<B>Bandwidth:</B> ";
	tooltips['iax_general'].en[12] = "<B>Enable Jitter Buffer:</B> ";
	tooltips['iax_general'].en[13] = "<B>Force Jitter Buffer:</B> ";
	tooltips['iax_general'].en[14] = "<B>Drop Count:</B> ";
	tooltips['iax_general'].en[15] = "<B>Max Jitter Buffer:</B> ";
	tooltips['iax_general'].en[16] = "<B>Max Interpolation Frames:</B> ";
	tooltips['iax_general'].en[17] = "<B>Resync Threshold:</B> ";
	tooltips['iax_general'].en[18] = "<B>Max Excess Buffer:</B> ";
	tooltips['iax_general'].en[19] = "<B>Min Excess Buffer:</B> ";
	tooltips['iax_general'].en[20] = "<B>Jitter Shrink Rate:</B> ";
	tooltips['iax_general'].en[21] = "<B>Trunk Freq:</B> ";
	tooltips['iax_general'].en[22] = "<B>Trunk Time Stamps:</B> ";
	tooltips['iax_general'].en[23] = "<B>Min Reg Expire:</B> ";
	tooltips['iax_general'].en[24] = "<B>Max Reg Expire:</B> ";
	tooltips['iax_general'].en[25] = "<B>IAX ThreadCount:</B> ";
	tooltips['iax_general'].en[26] = "<B>IAX Max ThreadCount:</B> ";
	tooltips['iax_general'].en[27] = "<B>Register:</B> ";
	tooltips['iax_general'].en[28] = "<B>Reg Context:</B> ";
	tooltips['iax_general'].en[29] = "<B>Auto Kill:</B> ";
	tooltips['iax_general'].en[30] = "<B>Authentication Debugging:</B> ";
	tooltips['iax_general'].en[31] = "<B>Codec Priority:</B> ";
	tooltips['iax_general'].en[32] = "<B>Type of Service:</B> ";
	tooltips['iax_general'].en[33] = "<B>Cache Friends:</B> ";
	tooltips['iax_general'].en[34] = "<B>Send Registry Updates:</B> ";
	tooltips['iax_general'].en[35] = "<B>Auto-Expire Friends:</B> ";
	tooltips['iax_general'].en[36] = "<B>Ignore Expired Peers:</B> ";
	tooltips['iax_general'].en[37] = "<B>Disallowed Codecs:</B> ";
	tooltips['iax_general'].en[38] = "<B>Allowed Codecs:</B> ";


	// Tooltips for Options (options)
	tooltips['options']= new Object;
	tooltips['options'].en = new Array;
	tooltips['options'].en[0] = "<B>Current Password:</B> Please enter your existing password";
	tooltips['options'].en[1] = "<B>New Password:</B> Enter the New Password";
	tooltips['options'].en[2] = "<B>Retype New Password:</B> Retype New Password ";
	tooltips['options'].en[3] = "<B>Bind Address:</B> The IP address to which the GUI will be assigned to.";
	tooltips['options'].en[4] = "<B>Port:</B> GUI port. Must be specified in browser while accessing the GUI";
	tooltips['options'].en[5] = "<B>HTTP Timeout:</B> Session time out in seconds";


	// Tooltips for status(status)
	tooltips['status']= new Object;
	tooltips['status'].en = new Array;
	tooltips['status'].en[0] = "<B>List of active channels:</B> Shows the list of active channels ";
	tooltips['status'].en[1] = "<B>Refresh:</B> Refresh the list of active channels";
	tooltips['status'].en[2] = "<B>Transfer:</B> Transfer selected channel";
	tooltips['status'].en[3] = "<B>Hangup:</B> Hangup selected Channel";

	// Tooltips for Service Providers (trunks)
	tooltips['trunks']= new Object;
	tooltips['trunks'].en = new Array;
	tooltips['trunks'].en[0] = "<B>Analog/Voip Trunks:</B> Analog lines are attached to analog interfaces of the PBX using FXO cards. Voice over IP (VoIP) connections are provided by an Internet Telephony Service Provider (ITSP).";
	tooltips['trunks'].en[1] = "<B>Provider:</B> Please select provider of your voice transport service.";
	tooltips['trunks'].en[2] = "<B>Lines:</B> Individual lines of the PBX Ex: Analog Port #3: The third analog port of the PBX.";
	tooltips['trunks'].en[3] = "<B>Username:</B> The username for your account with the provider - please contact your provider if you do not know it.";
	tooltips['trunks'].en[4] = "<B>Password:</B> The password for your account with the provider - please contact your provider if you do not know it.";
	tooltips['trunks'].en[5] = "<B>Digital Cards:</B> Digital Card trunking setup includes TExxxx based cards. Anything that is based from zaptel.conf and zapata.conf is readily availible to be configured as a trunk.";
	tooltips['trunks'].en[6] = "<B>Provider:</B> Digium Certified Internet Service Providers. Custom integrated into the GUI for simple setup";
	tooltips['trunks'].en[7] = "<B>Ngt Host:</B> This is the IP of the SIP server provided by NGT for your specific user account.";

	// Tooltips for Voicemenus (menus)
	tooltips['menus']= new Object;
	tooltips['menus'].en = new Array;
	tooltips['menus'].en[0] = "<B>Name:</B> A name for the Voice Menu";
	tooltips['menus'].en[1] = "<B>Steps:</B> A listing of the actions performed when a call enters the menu.";
	tooltips['menus'].en[2] = "<B>Add a new step:</B>Add additional steps performed during the menu.";
	tooltips['menus'].en[3] = "<B>Dial other Extensions:</B>Is the caller allowed to dial extensions other than the ones defined below?";
	tooltips['menus'].en[4] = "<B>Keypress Events:</B>Define the actions that occur when a user presses the corresponding digit.";
	tooltips['menus'].en[5] = "<B>Extension(optional):</B> If you want this Voicemenu to be accessible by dialing an extension, then enter that extension number";
	tooltips['menus'].en[6] = "<B>t</B> On Time out";
	tooltips['menus'].en[7] = "<B>i</B> On Invalid Input";
	
	// Tooltips for Calling Rules  (numberplan)
	tooltips['callingrules']= new Object;
	tooltips['callingrules'].en = new Array;
	tooltips['callingrules'].en[0] = "<B>new:</B> Add a new DialPlan. A DialPlan is a set of calling rules that can be assigned to one or more User Extensions.";
	tooltips['callingrules'].en[1] = "<B>delete:</B> Delete the selected DialPlan.";
	tooltips['callingrules'].en[2] = "<B>Edit:</B> Edit the selected Calling Rule.";
	tooltips['callingrules'].en[3] = "<B>Delete:</B> Delete the selected Calling Rule.";
	tooltips['callingrules'].en[4] = "<B>Add a Calling Rule:</B> Add new 'Calling Rule' to the selected DialPlan. A DialPlan is a set of calling rules, that can be assigned to one or more User Extensions.";
	tooltips['callingrules'].en[5] = "<B>Rule Name:</B> A name for this Calling Rule. Ex: 'Local' or 'Long Distance' etc.";
	tooltips['callingrules'].en[6] = "Select a Service Provider through which this call should be placed.";
	tooltips['callingrules'].en[7] = "<B>Dialing Rules:</B> Ex: If the number begins with <I>'256'</I> and followed by <I>7</I> digits <i>or more</I>";
	tooltips['callingrules'].en[8] = "<B>Custom Pattern:</B> Ex:  _91NXXNXXXXXX ";
	tooltips['callingrules'].en[9] = "Ex: Strip <i>1</i> digits from the front and prepend <i>256</i> before dialing";
	tooltips['callingrules'].en[10] = "Parked Calls: Check if you want to be able to access the parking lot from this Number Plan";

	// Tooltips for Incoming Calls (incoming)
	tooltips['incoming']= new Object;
	tooltips['incoming'].en = new Array;
	tooltips['incoming'].en[0] = "<B>Add a Incoming Rule:</B> Define a new Rule for handling Incoming calls based on service provider and/or the number called.";
	tooltips['incoming'].en[1] = "<B>Pattern:</B> Pattern of the DID number, <i>not</I> the pattern for the CID (caller id number)";


	// Tooltips for Record a Menu (record)
	tooltips['record']= new Object;
	tooltips['record'].en = new Array;
	tooltips['record'].en[0] = "<B>Record a new Voice Menu:</B> Lets you record a new voice menu using any user extension device";
	tooltips['record'].en[1] = "<B>Filename:</B> File name under which the recorded file should be saved to. Ex: MainGreeting ";
	tooltips['record'].en[2] = "<B>Extension used for recording:</B> Select a device through which this voice menu will be recorded.";


	// Tooltips for System Information  (sysinfo)
	tooltips['sysinfo']= new Object;
	tooltips['sysinfo'].en = new Array;
	tooltips['sysinfo'].en[0] = "<B>General:</B> Information about OS, Uptime, Asterisk, Date, Timezone and Hostname";
	tooltips['sysinfo'].en[1] = "<B>ifconfig:</B> Network devices information (ifconfig)";
	tooltips['sysinfo'].en[2] = "<B>Resources:</B> Disk and Memory usage information";
	tooltips['sysinfo'].en[3] = "<B>Logs:</B> Asterisk Log files";

	tooltips['graph']= new Object;
	tooltips['graph'].en = new Array;
	tooltips['graph'].en[0] = "<B>CPU Usage:</B> Real-Time Updating Graph For CPU Usage";


//	Tooltips for http_options.html in english
	tooltips['http_options']= new Object;
	tooltips['http_options'].en = new Array;

	tooltips['http_options'].en[0] = "" ;
	tooltips['http_options'].en[1] = "<B>Bind IP:</B> GUI will be available only on this IP address, if not sure please enter the LAN IP address. If you want the GUI to be available on all interfaces - enter 0.0.0.0" ;
	tooltips['http_options'].en[2] = "<B>Port:</B> Please enter the port number on which you want to access the GUI." ;


// 	Tooltips for the CDR reader page.
	tooltips['cdr'] = new Object;
	tooltips['cdr'].en = new Array;
	tooltips['cdr'].en[0] = "<B>View:</B> Select how many call detail records to read at once.." ;

//	Tooltips for the Digital Card page.
	tooltips['digital'] = new Object;
	tooltips['digital'].en = new Array;
	tooltips['digital'].en[0] = "<B>Framing/Coding:</B> To see this requires rev: 2986 of the 1.4 branch of zaptel.";
	tooltips['digital'].en[1] = "<B>Line Build Out:</B> To see this requires rev: 2986 of the 1.4 branch of zaptel.";
	tooltips['digital'].en['Out Of Alarm:'] = "<B>Alarm:</B>This setting allows the user to see if the span is currently in the alarm state of 'OK' and useable";
	tooltips['digital'].en['Alarms:'] = "<B>Alarms:</B>This allows the user to see the currently alarm status of the span";
	tooltips['digital'].en['Card Description:'] = "<B>Card Description:</B> This allows the user to check the description of the Digital Card.<br>(Often times will display the card type (4xx,2xx,1xx))";
	tooltips['digital'].en['Card Name:'] = "<B>Card Name:</B> Official name of the card, often displaying the total spans, card number, and current span.";
	tooltips['digital'].en['Total Channels:'] = "<B>Total Channels:</B> This is the count of the TOTAL channels availible on a particular span, not just the configured ones.";
	tooltips['digital'].en['Framing/Coding:'] = "<B>Framing/Coding:</B> Drop down box for enabling the changing of Framing/Coding. The first option is your current Framing/Coding";
	tooltips['digital'].en['Line Build Out:'] = "<B>Line Build Out:</B> The current LBO (Line Build Out) of the span.";
	tooltips['digital'].en['Sync Source:'] = "<B>Sync Source:</B> Your Zaptel Sync Source. Can be one of any spans, or 0 for non master";
	tooltips['digital'].en['Options:'] = "<B>Options:</B> Span Related Options, including Signalling, Switchtype, Channels, etc";

	
