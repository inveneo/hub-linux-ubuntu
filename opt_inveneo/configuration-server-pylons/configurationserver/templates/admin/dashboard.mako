<span class="h2">Dashboard for ${c.Server.name} Server</span>
</p>
Server On:
<b>
%if c.Server.server_on:
YES
% else:
NO
% endif
</b>
${h.form(h.url(controller='admin', action='set_server_on', id=c.Server.id), method='post')}
	<input type="submit" value="Toggle" class="button" />
${h.end_form()}
</p>
${h.form(h.url(controller='admin', action='set_initial_config'), method='get')}
	<p><input type="submit" value="Set Initial Config" class="button" /></p>
${h.end_form()}
</p>
${h.form(h.url(controller='admin', action='list'), method='get')}
	<p><input type="submit" value="List Configurations" class="button" /></p>
${h.end_form()}
</p>
${h.form(h.url(controller='admin', action='reset_client_config', id='deaddeadbeef'), method='post')}
	<p><input type="submit" value="Reset Client Config" class="button" /></p>
${h.end_form()}
</p>

