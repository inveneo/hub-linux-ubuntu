<span class="h3">Configuration </span>
</p>
${h.form(h.url(controller='admin', action='config_edit_process', id=c.Config.id), method='post')}
<!-- ${h.start_form('/admin/config_edit_process')} -->

<table>
<tr>
<td>MAC:</td>
<td>${h.text_field('mac', value=c.Config.mac)}</td>
% if c.Error and c.Error.has_key('mac'):
     <td><b>${c.Error['mac']}<b></td>
% endif
</tr>
<tr>
<td>TimeZone:</td>
<td>${h.text_field('timezone', value=c.Config.timezone)}</td>
</tr>
<td>NTP On:</td>
<td>${h.check_box('ntp_on', checked=c.Config.ntp_on)}</td>
</tr>
<tr>
<td>NTP Servers:</td>
<td>${h.text_field('ntp_servers', value=c.Config.ntp_servers)}</td>
</tr>
<tr>
<td>Proxy On:</td>
<td>${h.check_box('proxy_on', checked=c.Config.proxy_on)}</td>
</tr>
<tr>
<td>HTTP Proxy:</td>
<td>${h.text_field('http_proxy', value=c.Config.http_proxy)}</td>
</tr>
<tr>
<td>HTTP Proxy Port:</td>
<td>${h.text_field('http_proxy_port', value=c.Config.http_proxy_port)}</td>
% if c.Error and c.Error.has_key('http_proxy_port'):
     <td><b>${c.Error['http_proxy_port']}<b></td>
% endif
</tr>
<tr>
<td>HTTPS Proxy:</td>
<td>${h.text_field('https_proxy', value=c.Config.https_proxy)}</td>
</tr>
<tr>
<td>HTTPS Proxy Port:</td>
<td>${h.text_field('https_proxy_port', value=c.Config.https_proxy_port)}</td>
% if c.Error and c.Error.has_key('https_proxy_port'):
     <td><b>${c.Error['https_proxy_port']}<b></td>
% endif
</tr>
<tr>
<td>FTP Proxy:</td>
<td>${h.text_field('ftp_proxy', value=c.Config.ftp_proxy)}</td>
</tr>
<tr>
<td>FTP Proxy Port:</td>
<td>${h.text_field('ftp_proxy_port', value=c.Config.ftp_proxy_port)}</td>
% if c.Error and c.Error.has_key('ftp_proxy_port'):
     <td><b>${c.Error['ftp_proxy_port']}<b></td>
% endif
</tr>
<tr>
<td>Phone Home On:</td>
<td>${h.check_box('phone_home_on', checked=c.Config.phone_home_on)}</td>
</tr>
<tr>
<td>Phone Home Reg:</td>
<td>${h.text_field('phone_home_reg', value=c.Config.phone_home_reg)}</td>
</tr>
<tr>
<td>Phone Home Checkin:</td>
<td>${h.text_field('phone_home_checkin', value=c.Config.phone_home_checkin)}</td>
</tr>
<tr>
<td>Locale:</td>
<td>${h.text_field('locale', value=c.Config.locale)}</td>
% if c.Error and c.Error.has_key('locale'):
     <td><b>${c.Error['locale']}<b></td>
% endif
</tr>
<tr>
<td>Single User Login:</td>
<td>${h.check_box('single_user_login', checked=c.Config.single_user_login)}</td>
</tr>
</table>
</p>
${h.submit('Persist')}
${h.end_form}
