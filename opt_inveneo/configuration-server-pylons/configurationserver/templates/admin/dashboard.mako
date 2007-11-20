<%include file="../header.mako"/>
<h3 class="header">Dashboard for ${c.Server.name} Server</h3>

Server On:
%if c.Server.server_on:
<span class="green inline">YES</span>
<span class="post_link">
${h.link_to('Switch Off', url=h.url(controller='admin', action='set_server_on', id=c.Server.id), method='post')}
</span>
% else:
<span class="red">NO</span>
<span class="post_link">
${h.link_to('Switch On', url=h.url(controller='admin', action='set_server_on', id=c.Server.id), method='post')}
</span>
% endif
<p/>
${h.form(h.url(controller='admin', action='set_initial_config'), method='get')}
	<p><input type="submit" value="Set Initial Config" class="button" /></p>
${h.end_form()}
</p>

<p>
${h.form(h.url(controller='admin', action='list_initial_configurations'), method='get')}
	<p><input type="submit" value="List Initial Configurations" class="button" /></p>
${h.end_form()}
</p>

<p>
${h.form(h.url(controller='admin', action='list_station_configurations'), method='get')}
	<p><input type="submit" value="List Station Configurations" class="button" /></p>
${h.end_form()}
</p>

<p>
${h.form(h.url(controller='admin', action='reset_client_config', id='deaddeadbeef'), method='post')}
	<p><input type="submit" value="Reset Client Config" class="button" onclick="return confirmSubmit()"/></p>
${h.end_form()}
</p>

