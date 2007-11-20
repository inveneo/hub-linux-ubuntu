<%include file="../header.mako"/>
<h3 class="header">Existing Station Configurations</h3>

<p>
Switch: 
<span class="post_link">
${h.link_to('All On', url=h.url(controller='configuration', action='set_all_stations_on', all_on='True'), method='post')}
</span>
<span class="post_link">
${h.link_to('All Off', url=h.url(controller='configuration', action='set_all_stations_on', all_on='False'), method='post')}
</span>
<p>
<br>

% for station in c.Stations:
        <span class="line"><b>Mac:</b>${station.mac}</span>
	<span class="line"><b>On:</b>
%if station.station_on:
<span class="green">YES</span>
<span class="post_link">
${h.link_to('Switch off', url=h.url(controller='configuration', action='set_station_on', id=station.mac), method='post')}
</span>
% else:
<span class="red">NO</span>
<span class="post_link">
${h.link_to('Switch on', url=h.url(controller='configuration', action='set_station_on', id=station.mac), method='post')}
</span>
% endif
</span>
<span class="post_link">
${h.link_to('Remove', url=h.url(controller='admin', action='station_remove', id=station.mac), method='post', confirm='Are you sure?')}
</span>
% endfor
