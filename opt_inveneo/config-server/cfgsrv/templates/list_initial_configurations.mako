<%include file="../header.mako"/>
<h3 class="header">Existing Initial Configurations</h3>

<p>
<span class="post_link">
${h.link_to('Create New', url=h.url(controller='admin', action='config_add'), method='get')}
</span>
</p>

% for config in c.Configs:
<div class="content">
<span class="line"><b>MAC:</b> ${config.mac} </span>
<span class="line"><b>Lang:</b> ${config.lang} </span>
<span class="line"><b>Language:</b> ${config.language} </span>
<span class="line"><b>Time Zone:</b> ${config.time_zone} </span>
<br/>
<span class="line"><b>Config Host:</b> ${config.config_host} </span>
<span class="line"><b>Config Host Type:</b> ${config.config_host_type} </span>
<br/>
<span class="line"><b>Proxy On:</b> ${config.proxy_on} </span>
<br/>
<span class="line"><b>NTP On:</b> ${config.ntp_on} </span>
<span class="line"><b>NTP Servers:</b> ${config.ntp_servers} </span>
<br/>
<span class="line"><b>Hub Docs Dirs On:</b> ${config.hub_docs_dirs_on} </span>
<span class="line"><b>Local Shared Docs Dir On:</b>
    ${config.local_shared_docs_dir_on} </span>
<span class="line"><b>Local User Docs Dir On:</b>
    ${config.local_user_docs_dir_on} </span>
<br/>
<span class="line"><b>Phone Home On:</b> ${config.phone_home_on} </span>
<span class="line"><b>Phone Home Reg URL:</b>
    ${config.phone_home_reg_url} </span>
<span class="line"><b>Phone Home Checkin URL:</b>
    ${config.phone_home_checkin_url} </span>
<p>
<span class="post_link">
${h.link_to('Edit', url=h.url(controller='admin', action='edit', id=config.id), method='post')}
</span>
%if not h.is_default_initial_config(config):
    <span class="post_link">
    ${h.link_to('Remove', url=h.url(controller='admin', action='config_remove', id=config.mac), method='post', confirm='Are you sure?')}
    </span>
%endif
</p>
<br>
</div>
% endfor
