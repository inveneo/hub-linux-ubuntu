<%inherit file="base.mako"/>

## helpers
<%def name="emit_text_field(key, variable)">
<tr>
<td align='right'>${key}:</td>
<td>${h.text_field(key, value=variable, size=54)}</td>
% if c.Error and c.Error.has_key(key):
    <td class="error">${c.Error[key]}</td>
% endif
</tr>
</%def>

<%def name="emit_check_box(key, variable)">
<tr>
<td align='right'>${key}:</td>
<td>${h.check_box(key, checked=variable)}</td>
</tr>
</%def>

<%def name="emit_select(key, variable, liszt)">
<tr>
<td align='right'>${key}:</td>
<td>${h.select(key, h.options_for_select(liszt, variable))}</td>
</tr>
</%def>

## here's the beef
<h3 class="header">Station Configuration</h3>
${h.form(h.url(controller='admin', action='edit_station', mac=c.Station.mac),
    method='post')}
<table cellpadding='2'>

<tr><td align='right'>MAC:</td><td>${c.Station.mac}</td></tr>

## <tr><td>ON:</td><td>${c.Station.on}</td></tr>

${emit_text_field('Hostname', c.Station.hostname)}
${emit_select('Language', c.Station.language, g.LANGS_LIST)}
${emit_text_field('Time Zone', c.Station.time_zone)}
${emit_check_box('NTP On', c.Station.ntp_on)}
${emit_text_field('NTP Servers', c.Station.ntp_servers)}
${emit_text_field('Config Host', c.Station.config_host)}
${emit_select('Config Host Type', c.Station.config_host_type, g.HOST_TYPES)}
${emit_check_box('Proxy On', c.Station.proxy_on)}
${emit_text_field('HTTP Proxy', c.Station.http_proxy)}
${emit_text_field('HTTP Proxy Port', c.Station.http_proxy_port)}
${emit_text_field('HTTPS Proxy', c.Station.https_proxy)}
${emit_text_field('HTTPS Proxy Port', c.Station.https_proxy_port)}
${emit_text_field('FTP Proxy', c.Station.ftp_proxy)}
${emit_text_field('FTP Proxy Port', c.Station.ftp_proxy_port)}
${emit_check_box('Local User Docs Dir On',
    c.Station.local_user_docs_dir_on)}
${emit_check_box('Local Shared Docs Dir On',
    c.Station.local_shared_docs_dir_on)}
${emit_check_box('Hub Docs Dirs On', c.Station.hub_docs_dirs_on)}
${emit_check_box('Phone Home On', c.Station.phone_home_on)}
${emit_text_field('Phone Home Reg URL',
    c.Station.phone_home_reg_url)}
${emit_text_field('Phone Home Checkin URL',
    c.Station.phone_home_checkin_url)}
${emit_text_field('Phone Home Latitude', c.Station.phone_home_latitude)}
${emit_text_field('Phone Home Longitude', c.Station.phone_home_longitude)}
</table>
## ${h.submit('Save')}
${h.end_form}

