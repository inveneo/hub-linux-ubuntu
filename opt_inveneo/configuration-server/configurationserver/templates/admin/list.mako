<span class="h3">Existing Configurations</span>
${h.form(h.url(controller='admin', action='config_add'), method='post')}
	<p><input type="submit" value="Create New" class="button" /></p>
${h.end_form()}
</p>
% for config in c.Configs:
<div class="content">
        <span class="line"><b>MAC:</b> ${config.mac} </span>
        <span class="line"><b>TimeZone:</b> ${config.timezone} </span>
        </br>
        <span class="line"><b>NTP On:</b> ${config.ntp_on} </span>
        <span class="line"><b>NTP Servers:</b> ${config.ntp_servers} </span>
        </br>
	<span class="line"><b>Proxy On:</b> ${config.proxy_on} </span>
        </br>
        <span class="line"><b>HTTP Proxy:</b> ${config.http_proxy} </span>
        <span class="line"><b>HTTP Proxy Port:</b> ${config.http_proxy_port} </span>
        </br>
        <span class="line"><b>HTTPS Proxy:</b> ${config.https_proxy} </span>
        <span class="line"><b>HTTPS Proxy Port:</b> ${config.https_proxy_port} </span>
        </br>
        <span class="line"><b>FTP Proxy:</b> ${config.ftp_proxy} </span>
        <span class="line"><b>FTP Proxy Port:</b> ${config.ftp_proxy_port} </span>
        </br>
        <span class="line"><b>Phone Home On:</b> ${config.phone_home_on} </span>
        <span class="line"><b>Phone Home Reg:</b> ${config.phone_home_reg} </span>
        <span class="line"><b>Phone Home Checkin:</b> ${config.phone_home_checkin} </span>
        </br>
        <span class="line"><b>Locale:</b> ${config.locale} </span>
        <span class="line"><b>Single User Login:</b> ${config.single_user_login} </span>
	</br>
	${h.form(h.url(controller='admin', action='edit', id=config.id), method='post')}
	<p><input type="submit" value="Edit" class="button" /></p>
${h.end_form()}
	</p>

</div>
% endfor
