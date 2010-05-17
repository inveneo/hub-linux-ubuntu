<%include file="../header.mako"/>
<h3 class="header">Set Initial Configuration</h3>
${h.form(h.url(controller='admin', action='config_edit_process', id=c.Config.id), method='post')}
<table>
<tr>
<td>MAC:</td>
%if not c.Edit:
     <td>${h.text_field('mac', value=c.Config.mac)}</td>
     % if c.Error and c.Error.has_key('mac'):
       <td class="error">${c.Error['mac']}</td>
     % endif
% else:
<td>${c.Config.mac}</td>
% endif
</tr>

<tr>
<td>Lang:</td>
<td>
${h.select('lang', h.options_for_select(h.get_langs_as_list(), c.Config.lang))}
</td>
% if c.Error and c.Error.has_key('lang'):
     <td><b>${c.Error['lang']}<b></td>
% endif
</tr>

<tr>
<td>Language:</td>
<td>
${ h.select('language',
    h.options_for_select(h.get_langs_as_list(), c.Config.language)) }
</td>
% if c.Error and c.Error.has_key('language'):
     <td><b>${c.Error['language']}<b></td>
% endif
</tr>

<tr>
<td>Time Zone:</td>
<td>
${ h.select('time_zone',
    h.options_for_select(h.get_timezones_as_string_list(),
        c.Config.time_zone)) }
</td>
</tr>

<tr>
<td>Config Host:</td>
<td>
${ h.text_field('config_host', value=c.Config.config_host) }
</td>
</tr>

<tr>
<td>Config Host Type:</td>
<td>
${ h.select('config_host_type',
    h.options_for_select(g.HOST_TYPES, c.Config.config_host_type)) }
</td>
</tr>

<tr>
<td>Proxy On:</td>
<td>
${h.check_box('proxy_on', checked=c.Config.proxy_on)}
</td>
</tr>

<tr>
<td>NTP On:</td>
<td>
${h.check_box('ntp_on', checked=c.Config.ntp_on)}
</td>
</tr>

<tr>
<td>NTP Servers:</td>
<td>
${h.text_field('ntp_servers', value=c.Config.ntp_servers)}
</td>
</tr>

<tr>
<td>Hub Docs Dirs On:</td>
<td>
${h.check_box('hub_docs_dirs_on', checked=c.Config.hub_docs_dirs_on)}
</td>
</tr>

<tr>
<td>Local Shared Docs Dir On:</td>
<td>
${h.check_box('local_shared_docs_dir_on',
    checked=c.Config.local_shared_docs_dir_on)}
</td>
</tr>

<tr>
<td>Local User Docs Dir On:</td>
<td>
${h.check_box('local_user_docs_dir_on',
    checked=c.Config.local_user_docs_dir_on)}
</td>
</tr>

<tr>
<td>Phone Home On:</td>
<td>
${h.check_box('phone_home_on', checked=c.Config.phone_home_on)}
</td>
</tr>

<tr>
<td>Phone Home Reg URL:</td>
<td>
${h.text_field('phone_home_reg_url', value=c.Config.phone_home_reg_url)}
</td>
</tr>

<tr>
<td>Phone Home Checkin URL:</td>
<td>
${h.text_field('phone_home_checkin_url', value=c.Config.phone_home_checkin_url)}
</td>
</tr>

</table>
<p/>
${h.submit('Save')}
${h.end_form}
