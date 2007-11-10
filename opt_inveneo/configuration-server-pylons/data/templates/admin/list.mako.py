from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1194652429.2151239
_template_filename='/home/rjocham/pylons/opt_inveneo/configuration-server-pylons/configurationserver/templates/admin/list.mako'
_template_uri='/admin/list.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = []


def render_body(context,**pageargs):
    context.caller_stack.push_frame()
    try:
        __M_locals = dict(pageargs=pageargs)
        h = context.get('h', UNDEFINED)
        c = context.get('c', UNDEFINED)
        # SOURCE LINE 1
        context.write(u'<span class="h3">Existing Configurations</span>\n')
        # SOURCE LINE 2
        context.write(unicode(h.form(h.url(controller='admin', action='dashboard'), method='get')))
        context.write(u'\n\t<p><input type="submit" value="Dashboard" class="button" /></p>\n')
        # SOURCE LINE 4
        context.write(unicode(h.end_form()))
        context.write(u'\n')
        # SOURCE LINE 5
        context.write(unicode(h.form(h.url(controller='admin', action='config_add'), method='get')))
        context.write(u'\n\t<p><input type="submit" value="Create New" class="button" /></p>\n')
        # SOURCE LINE 7
        context.write(unicode(h.end_form()))
        context.write(u'\n</p>\n')
        # SOURCE LINE 9
        for config in c.Configs:
            # SOURCE LINE 10
            context.write(u'<div class="content">\n        <span class="line"><b>MAC:</b> ')
            # SOURCE LINE 11
            context.write(unicode(config.mac))
            context.write(u' </span>\n        <span class="line"><b>TimeZone:</b> ')
            # SOURCE LINE 12
            context.write(unicode(config.timezone))
            context.write(u' </span>\n        </br>\n        <span class="line"><b>NTP On:</b> ')
            # SOURCE LINE 14
            context.write(unicode(config.ntp_on))
            context.write(u' </span>\n        <span class="line"><b>NTP Servers:</b> ')
            # SOURCE LINE 15
            context.write(unicode(config.ntp_servers))
            context.write(u' </span>\n        </br>\n\t<span class="line"><b>Proxy On:</b> ')
            # SOURCE LINE 17
            context.write(unicode(config.proxy_on))
            context.write(u' </span>\n        </br>\n        <span class="line"><b>HTTP Proxy:</b> ')
            # SOURCE LINE 19
            context.write(unicode(config.http_proxy))
            context.write(u' </span>\n        <span class="line"><b>HTTP Proxy Port:</b> ')
            # SOURCE LINE 20
            context.write(unicode(config.http_proxy_port))
            context.write(u' </span>\n        </br>\n        <span class="line"><b>HTTPS Proxy:</b> ')
            # SOURCE LINE 22
            context.write(unicode(config.https_proxy))
            context.write(u' </span>\n        <span class="line"><b>HTTPS Proxy Port:</b> ')
            # SOURCE LINE 23
            context.write(unicode(config.https_proxy_port))
            context.write(u' </span>\n        </br>\n        <span class="line"><b>FTP Proxy:</b> ')
            # SOURCE LINE 25
            context.write(unicode(config.ftp_proxy))
            context.write(u' </span>\n        <span class="line"><b>FTP Proxy Port:</b> ')
            # SOURCE LINE 26
            context.write(unicode(config.ftp_proxy_port))
            context.write(u' </span>\n        </br>\n        <span class="line"><b>Phone Home On:</b> ')
            # SOURCE LINE 28
            context.write(unicode(config.phone_home_on))
            context.write(u' </span>\n        <span class="line"><b>Phone Home Reg:</b> ')
            # SOURCE LINE 29
            context.write(unicode(config.phone_home_reg))
            context.write(u' </span>\n        <span class="line"><b>Phone Home Checkin:</b> ')
            # SOURCE LINE 30
            context.write(unicode(config.phone_home_checkin))
            context.write(u' </span>\n        </br>\n        <span class="line"><b>Locale:</b> ')
            # SOURCE LINE 32
            context.write(unicode(config.locale))
            context.write(u' </span>\n        <span class="line"><b>Single User Login:</b> ')
            # SOURCE LINE 33
            context.write(unicode(config.single_user_login))
            context.write(u' </span>\n\t</br>\n\t')
            # SOURCE LINE 35
            context.write(unicode(h.form(h.url(controller='admin', action='edit', id=config.id), method='post')))
            context.write(u'\n\t<p><input type="submit" value="Edit" class="button" /></p>\n')
            # SOURCE LINE 37
            context.write(unicode(h.end_form()))
            context.write(u'\n\t</p>\n\n</div>\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


