from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1194463426.7831521
_template_filename='/home/rjocham/pylons/opt_inveneo/configuration-server-pylons/configurationserver/templates/admin/config_edit.mako'
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
        context.write(unicode(h.form(h.url(controller='admin', action='config_edit_process', id=c.Config.id), method='post')))
        context.write(u'\n<!-- ')
        # SOURCE LINE 4
        context.write(unicode(h.start_form('/admin/config_edit_process')))
        context.write(u' -->\n\n<table>\n<tr>\n<td>MAC:</td>\n<td>')
        # SOURCE LINE 9
        context.write(unicode(h.text_field('mac', value=c.Config.mac)))
        context.write(u'</td>\n')
        # SOURCE LINE 10
        if c.Error and c.Error.has_key('mac'):
            # SOURCE LINE 11
            context.write(u'     <td><b>')
            context.write(unicode(c.Error['mac']))
            context.write(u'<b></td>\n')
        # SOURCE LINE 13
        context.write(u'</tr>\n<tr>\n<td>TimeZone:</td>\n<td>')
        # SOURCE LINE 16
        context.write(unicode(h.text_field('timezone', value=c.Config.timezone)))
        context.write(u'</td>\n</tr>\n<td>NTP On:</td>\n<td>')
        # SOURCE LINE 19
        context.write(unicode(h.check_box('ntp_on', checked=c.Config.ntp_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>NTP Servers:</td>\n<td>')
        # SOURCE LINE 23
        context.write(unicode(h.text_field('ntp_servers', value=c.Config.ntp_servers)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Proxy On:</td>\n<td>')
        # SOURCE LINE 27
        context.write(unicode(h.check_box('proxy_on', checked=c.Config.proxy_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTP Proxy:</td>\n<td>')
        # SOURCE LINE 31
        context.write(unicode(h.text_field('http_proxy', value=c.Config.http_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTP Proxy Port:</td>\n<td>')
        # SOURCE LINE 35
        context.write(unicode(h.text_field('http_proxy_port', value=c.Config.http_proxy_port)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTPS Proxy:</td>\n<td>')
        # SOURCE LINE 39
        context.write(unicode(h.text_field('https_proxy', value=c.Config.https_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTPS Proxy Port:</td>\n<td>')
        # SOURCE LINE 43
        context.write(unicode(h.text_field('https_proxy_port', value=c.Config.https_proxy_port)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>FTP Proxy:</td>\n<td>')
        # SOURCE LINE 47
        context.write(unicode(h.text_field('ftp_proxy', value=c.Config.ftp_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>FTP Proxy Port:</td>\n<td>')
        # SOURCE LINE 51
        context.write(unicode(h.text_field('ftp_proxy_port', value=c.Config.ftp_proxy_port)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Phone Home On:</td>\n<td>')
        # SOURCE LINE 55
        context.write(unicode(h.check_box('phone_home_on', checked=c.Config.phone_home_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Phone Home Reg:</td>\n<td>')
        # SOURCE LINE 59
        context.write(unicode(h.text_field('phone_home_reg', value=c.Config.phone_home_reg)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Phone Home Checkin:</td>\n<td>')
        # SOURCE LINE 63
        context.write(unicode(h.text_field('phone_home_checkin', value=c.Config.phone_home_checkin)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Locale:</td>\n<td>')
        # SOURCE LINE 67
        context.write(unicode(h.text_field('locale', value=c.Config.locale)))
        context.write(u'</td>\n')
        # SOURCE LINE 68
        if c.Error and c.Error.has_key('locale'):
            # SOURCE LINE 69
            context.write(u'     <td><b>')
            context.write(unicode(c.Error['locale']))
            context.write(u'<b></td>\n')
        # SOURCE LINE 71
        context.write(u'</tr>\n<tr>\n<td>Single User Login:</td>\n<td>')
        # SOURCE LINE 74
        context.write(unicode(h.check_box('single_user_login', checked=c.Config.single_user_login)))
        context.write(u'</td>\n</tr>\n</table>\n</p>\n')
        # SOURCE LINE 78
        context.write(unicode(h.submit('Persist')))
        context.write(u'\n')
        # SOURCE LINE 79
        context.write(unicode(h.end_form))
        context.write(u'\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


