<%inherit file="../base.mako"/>

<h3 class="header">Configuration Server</h3>
<p>
Server Enabled:
%if c.Server.server_on:
<span class="green inline">YES</span>
<span class="post_link">
${h.link_to('Disable',
    url=h.url(controller='admin', action='set_server_on', id=c.Server.name),
    method='post')}
</span>
% else:
<span class="red">NO</span>
<span class="post_link">
${h.link_to('Enable',
    url=h.url(controller='admin', action='set_server_on', id=c.Server.name),
    method='post')}
</span>
% endif
</p>

<h3 class="header">Station Configuration</h3>
${h.form(h.url(controller='admin', action='config_edit_process',
    id=c.Station.mac), method='post')}
<table>
${emit_text_field('mac', c.Station.mac)}
${emit_check_box('on', c.Station.on)}
${emit_text_field('hostname', c.Station.hostname)}
${emit_select('language', c.Station.language, g.LANGS_LIST)}
${emit_select('time_zone', c.Station.time_zone,
    h.get_timezones_as_string_list())}
${emit_check_box('ntp_on', c.Station.ntp_on)}
${emit_text_field('ntp_servers', c.Station.ntp_servers)}
${emit_text_field('config_host', c.Station.config_host)}
${emit_select('config_host_type', c.Station.config_host_type, g.HOST_TYPES)}
${emit_check_box('proxy_on', c.Station.proxy_on)}
${emit_text_field('http_proxy', c.Station.http_proxy)}
${emit_text_field('http_proxy_port', c.Station.http_proxy_port)}
${emit_text_field('https_proxy', c.Station.https_proxy)}
${emit_text_field('https_proxy_port', c.Station.https_proxy_port)}
${emit_text_field('ftp_proxy', c.Station.ftp_proxy)}
${emit_text_field('ftp_proxy_port', c.Station.ftp_proxy_port)}
${emit_check_box('local_user_docs_dir_on', c.Station.local_user_docs_dir_on)}
${emit_check_box('local_shared_docs_dir_on',
    c.Station.local_shared_docs_dir_on)}
${emit_check_box('hub_docs_dirs_on', c.Station.hub_docs_dirs_on)}
${emit_check_box('phone_home_on', c.Station.phone_home_on)}
${emit_text_field('phone_home_reg_url', c.Station.phone_home_reg_url)}
${emit_text_field('phone_home_checkin_url', c.Station.phone_home_checkin_url)}
${emit_text_field('phone_home_latitude', c.Station.phone_home_latitude)}
${emit_text_field('phone_home_longitude', c.Station.phone_home_longitude)}
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
