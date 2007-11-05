from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1194241065.5846579
_template_filename='/home/rjocham/pylons/configuration-server/configurationserver/templates/admin/config_edit.mako'
_template_uri='/admin/config_edit.mako'
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
        context.write(u'<span class="h3">Configuration </span>\n</p>\n')
        # SOURCE LINE 3
        context.write(unicode(h.form(h.url(controller='admin', action='config_edit_process', config_id=c.Config.id), method='post')))
        context.write(u'\n<!-- ')
        # SOURCE LINE 4
        context.write(unicode(h.start_form('/admin/config_edit_process')))
        context.write(u' -->\n\n<table>\n<tr>\n<td>MAC:</td>\n<td>')
        # SOURCE LINE 9
        context.write(unicode(h.text_field('mac', value=c.Config.mac)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>TimeZone:</td>\n<td>')
        # SOURCE LINE 13
        context.write(unicode(h.text_field('timezone', value=c.Config.timezone)))
        context.write(u'</td>\n</tr>\n<td>NTP On:</td>\n<td>')
        # SOURCE LINE 16
        context.write(unicode(h.check_box('ntp_on', checked=c.Config.ntp_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>NTP Servers:</td>\n<td>')
        # SOURCE LINE 20
        context.write(unicode(h.text_field('ntp_servers', value=c.Config.ntp_servers)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Proxy On:</td>\n<td>')
        # SOURCE LINE 24
        context.write(unicode(h.check_box('proxy_on', checked=c.Config.proxy_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTP Proxy:</td>\n<td>')
        # SOURCE LINE 28
        context.write(unicode(h.text_field('http_proxy', value=c.Config.http_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTP Proxy Port:</td>\n<td>')
        # SOURCE LINE 32
        context.write(unicode(h.text_field('http_proxy_port', value=c.Config.http_proxy_port)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTPS Proxy:</td>\n<td>')
        # SOURCE LINE 36
        context.write(unicode(h.text_field('https_proxy', value=c.Config.https_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTPS Proxy Port:</td>\n<td>')
        # SOURCE LINE 40
        context.write(unicode(h.text_field('https_proxy_port', value=c.Config.https_proxy_port)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>FTP Proxy:</td>\n<td>')
        # SOURCE LINE 44
        context.write(unicode(h.text_field('ftp_proxy', value=c.Config.ftp_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>FTP Proxy Port:</td>\n<td>')
        # SOURCE LINE 48
        context.write(unicode(h.text_field('ftp_proxy_port', value=c.Config.ftp_proxy_port)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Phone Home On:</td>\n<td>')
        # SOURCE LINE 52
        context.write(unicode(h.check_box('phone_home_on', checked=c.Config.phone_home_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Phone Home Reg:</td>\n<td>')
        # SOURCE LINE 56
        context.write(unicode(h.text_field('phone_home_reg', value=c.Config.phone_home_reg)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Phone Home Checkin:</td>\n<td>')
        # SOURCE LINE 60
        context.write(unicode(h.text_field('phone_home_checkin', value=c.Config.phone_home_checkin)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Locale:</td>\n<td>')
        # SOURCE LINE 64
        context.write(unicode(h.text_field('locale', value=c.Config.locale)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Single User Login:</td>\n<td>')
        # SOURCE LINE 68
        context.write(unicode(h.check_box('single_user_login', checked=c.Config.single_user_login)))
        context.write(u'</td>\n</tr>\n</table>\n</p>\n')
        # SOURCE LINE 72
        context.write(unicode(h.submit('Persist')))
        context.write(u'\n')
        # SOURCE LINE 73
        context.write(unicode(h.end_form))
        context.write(u'\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


