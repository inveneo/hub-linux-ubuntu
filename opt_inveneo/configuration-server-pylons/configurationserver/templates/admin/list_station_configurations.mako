<%include file="../header.mako"/>
<h3>Existing Station Configurations</h3>
${h.form(h.url(controller='configuration', action='set_all_stations_on', all_on='True'), method='post')}
<input type="submit" value="All On" class="button" />
${h.end_form()}
${h.form(h.url(controller='configuration', action='set_all_stations_on', all_on='False'), method='post')}
<input type="submit" value="All Off" class="button" />
${h.end_form()}
<p/>
</br>
% for station in c.Stations:
<div class="content">
        <span class="line"><b>Mac:</b>${station.mac}</span>
	<span class="line"><b>On:</b>
%if station.station_on:
YES
% else:
NO
% endif
</span>
${h.form(h.url(controller='configuration', action='set_station_on', id=station.mac), method='post')}
<input type="submit" value="Toggle" class="button" />
${h.end_form()}
${h.form(h.url(controller='admin', action='station_remove', id=station.mac), method='post')}
<input type="submit" value="Remove" class="button" onclick="return confirmSubmit()"/>
${h.end_form()}
<p/>
</div>
% endfor
