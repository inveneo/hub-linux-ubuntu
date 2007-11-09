<span class="h3">Dashboard</span>
${h.form(h.url(controller='admin', action='set_initial_config'), method='post')}
	<p><input type="submit" value="Set Initial Config" class="button" /></p>
${h.end_form()}
</p>
${h.form(h.url(controller='admin', action='list'), method='post')}
	<p><input type="submit" value="List Configurations" class="button" /></p>
${h.end_form()}
</p>
${h.form(h.url(controller='admin', action='reset_client_config', id='deaddeadbeef'), method='post')}
	<p><input type="submit" value="Reset Client Config" class="button" /></p>
${h.end_form()}
