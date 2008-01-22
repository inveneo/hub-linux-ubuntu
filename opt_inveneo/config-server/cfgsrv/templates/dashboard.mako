<%inherit file="base.mako"/>

<h3 class="header">Configuration Server</h3>
<p>
Automated Configuration Service:
%if c.Server.server_on:
<span class="green inline">ON</span>
<span class="post_link">
${h.link_to('Turn Off',
    url=h.url(controller='admin', action='toggle_server', name=c.Server.name),
    method='post')}
</span>
% else:
<span class="red">OFF</span>
<span class="post_link">
${h.link_to('Turn On',
    url=h.url(controller='admin', action='toggle_server', name=c.Server.name),
    method='post')}
</span>
% endif
</p>

<p>
${h.link_to('Reset', url=h.url(controller='admin', action='reset_stations'),
    confirm='Are you sure?')} all desktops to default (factory) configuration
</p>

<h3 class="header">Station Configuration</h3>
${h.form(h.url(controller='admin', action='edit_station', mac=c.Station.mac),
    method='post')}
<table>
<tr>
<td>MAC:</td>
<td>${c.Station.mac}</td>
</tr>
<tr>
<td>ON:</td>
<td>${c.Station.on}</td>
</tr>
${emit_text_field('INV_HOSTNAME', c.Station.hostname)}
${emit_select('INV_LANG', c.Station.language, g.LANGS_LIST)}
${emit_text_field('INV_TIME_ZONE', c.Station.time_zone)}
${emit_check_box('INV_NTP_ON', c.Station.ntp_on)}
${emit_text_field('INV_NTP_SERVERS', c.Station.ntp_servers)}
${emit_text_field('INV_CONFIG_HOST', c.Station.config_host)}
${emit_select('INV_CONFIG_HOST_TYPE', c.Station.config_host_type, g.HOST_TYPES)}
${emit_check_box('INV_PROXY_ON', c.Station.proxy_on)}
${emit_text_field('INV_HTTP_PROXY', c.Station.http_proxy)}
${emit_text_field('INV_HTTP_PROXY_PORT', c.Station.http_proxy_port)}
${emit_text_field('INV_HTTPS_PROXY', c.Station.https_proxy)}
${emit_text_field('INV_HTTPS_PROXY_PORT', c.Station.https_proxy_port)}
${emit_text_field('INV_FTP_PROXY', c.Station.ftp_proxy)}
${emit_text_field('INV_FTP_PROXY_PORT', c.Station.ftp_proxy_port)}
${emit_check_box('INV_LOCAL_USER_DOCS_DIR_ON',
    c.Station.local_user_docs_dir_on)}
${emit_check_box('INV_LOCAL_SHARED_DOCS_DIR_ON',
    c.Station.local_shared_docs_dir_on)}
${emit_check_box('INV_HUB_DOCS_DIRS_ON', c.Station.hub_docs_dirs_on)}
${emit_check_box('INV_PHONE_HOME_ON', c.Station.phone_home_on)}
${emit_text_field('INV_PHONE_HOME_REG_URL',
    c.Station.phone_home_reg_url)}
${emit_text_field('INV_PHONE_HOME_CHECKIN_URL',
    c.Station.phone_home_checkin_url)}
${emit_text_field('INV_PHONE_HOME_LATITUDE', c.Station.phone_home_latitude)}
${emit_text_field('INV_PHONE_HOME_LONGITUDE', c.Station.phone_home_longitude)}
</table>
${h.submit('Save')}
${h.end_form}

<%def name="emit_text_field(key, variable)">
<tr>
<td>${key}:</td>
<td>${h.text_field(key, value=variable, size=54)}</td>
% if c.Error and c.Error.has_key(key):
    <td class="error">${c.Error[key]}</td>
% endif
</tr>
</%def>

<%def name="emit_check_box(key, variable)">
<tr>
<td>${key}:</td>
<td>${h.check_box(key, checked=variable)}</td>
</tr>
</%def>

<%def name="emit_select(key, variable, liszt)">
<tr>
<td>${key}:</td>
<td>${h.select(key, h.options_for_select(liszt, variable))}</td>
</tr>
</%def>

