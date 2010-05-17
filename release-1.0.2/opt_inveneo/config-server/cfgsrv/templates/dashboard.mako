<%inherit file="base.mako"/>
<p>
Automated configuration service is
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
<span class="post_link">
${h.link_to('Reset', url=h.url(controller='admin', action='reset_stations'),
    confirm='Are you sure?')}
</span>
all desktops to default (factory) configuration
</p>

<p>
${h.link_to('View', url=h.url(controller='admin', action='display_station'))}
global station configuration
</p>
