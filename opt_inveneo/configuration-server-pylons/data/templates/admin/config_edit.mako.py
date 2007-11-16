from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1195106533.409163
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
        runtime._include_file(context, u'../header.mako', _template_uri)
        context.write(u'\n<h3>Set Initial Configuration</h3>\n')
        # SOURCE LINE 3
        context.write(unicode(h.form(h.url(controller='admin', action='config_edit_process', id=c.Config.id), method='post')))
        context.write(u'\n<table>\n<tr>\n<td>MAC:</td>\n')
        # SOURCE LINE 7
        if not c.Edit:
            # SOURCE LINE 8
            context.write(u'     <td>')
            context.write(unicode(h.text_field('mac', value=c.Config.mac)))
            context.write(u'</td>\n')
            # SOURCE LINE 9
            if c.Error and c.Error.has_key('mac'):
                # SOURCE LINE 10
                context.write(u'       <td><b>')
                context.write(unicode(c.Error['mac']))
                context.write(u'<b></td>\n')
            # SOURCE LINE 12
        else:
            # SOURCE LINE 13
            context.write(u'<td>')
            context.write(unicode(c.Config.mac))
            context.write(u'</td>\n')
        # SOURCE LINE 15
        context.write(u'</tr>\n<tr>\n<td>Time Zone:</td>\n<td>\n')
        # SOURCE LINE 19
        context.write(unicode( h.select('timezone', h.options_for_select(h.get_timezones_as_string_list(), c.Config.timezone)) ))
        context.write(u'\n</td>\n</tr>\n<td>NTP On:</td>\n<td>')
        # SOURCE LINE 23
        context.write(unicode(h.check_box('ntp_on', checked=c.Config.ntp_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>NTP Servers:</td>\n<td>')
        # SOURCE LINE 27
        context.write(unicode(h.text_field('ntp_servers', value=c.Config.ntp_servers)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Proxy On:</td>\n<td>')
        # SOURCE LINE 31
        context.write(unicode(h.check_box('proxy_on', checked=c.Config.proxy_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTP Proxy:</td>\n<td>')
        # SOURCE LINE 35
        context.write(unicode(h.text_field('http_proxy', value=c.Config.http_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTP Proxy Port:</td>\n<td>')
        # SOURCE LINE 39
        context.write(unicode(h.text_field('http_proxy_port', value=c.Config.http_proxy_port)))
        context.write(u'</td>\n')
        # SOURCE LINE 40
        if c.Error and c.Error.has_key('http_proxy_port'):
            # SOURCE LINE 41
            context.write(u'     <td><b>')
            context.write(unicode(c.Error['http_proxy_port']))
            context.write(u'<b></td>\n')
        # SOURCE LINE 43
        context.write(u'</tr>\n<tr>\n<td>HTTPS Proxy:</td>\n<td>')
        # SOURCE LINE 46
        context.write(unicode(h.text_field('https_proxy', value=c.Config.https_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTPS Proxy Port:</td>\n<td>')
        # SOURCE LINE 50
        context.write(unicode(h.text_field('https_proxy_port', value=c.Config.https_proxy_port)))
        context.write(u'</td>\n')
        # SOURCE LINE 51
        if c.Error and c.Error.has_key('https_proxy_port'):
            # SOURCE LINE 52
            context.write(u'     <td><b>')
            context.write(unicode(c.Error['https_proxy_port']))
            context.write(u'<b></td>\n')
        # SOURCE LINE 54
        context.write(u'</tr>\n<tr>\n<td>FTP Proxy:</td>\n<td>')
        # SOURCE LINE 57
        context.write(unicode(h.text_field('ftp_proxy', value=c.Config.ftp_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>FTP Proxy Port:</td>\n<td>')
        # SOURCE LINE 61
        context.write(unicode(h.text_field('ftp_proxy_port', value=c.Config.ftp_proxy_port)))
        context.write(u'</td>\n')
        # SOURCE LINE 62
        if c.Error and c.Error.has_key('ftp_proxy_port'):
            # SOURCE LINE 63
            context.write(u'     <td><b>')
            context.write(unicode(c.Error['ftp_proxy_port']))
            context.write(u'<b></td>\n')
        # SOURCE LINE 65
        context.write(u'</tr>\n<tr>\n<td>Phone Home On:</td>\n<td>')
        # SOURCE LINE 68
        context.write(unicode(h.check_box('phone_home_on', checked=c.Config.phone_home_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Phone Home Reg:</td>\n<td>')
        # SOURCE LINE 72
        context.write(unicode(h.text_field('phone_home_reg', value=c.Config.phone_home_reg)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Phone Home Checkin:</td>\n<td>')
        # SOURCE LINE 76
        context.write(unicode(h.text_field('phone_home_checkin', value=c.Config.phone_home_checkin)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Locale:</td>\n<td>\n')
        # SOURCE LINE 81
        context.write(unicode( h.select('locale', h.options_for_select(h.get_locales_as_list(), c.Config.locale)) ))
        context.write(u'\n</td>\n')
        # SOURCE LINE 83
        if c.Error and c.Error.has_key('locale'):
            # SOURCE LINE 84
            context.write(u'     <td><b>')
            context.write(unicode(c.Error['locale']))
            context.write(u'<b></td>\n')
        # SOURCE LINE 86
        context.write(u'</tr>\n<tr>\n<td>Single User Login:</td>\n<td>')
        # SOURCE LINE 89
        context.write(unicode(h.check_box('single_user_login', checked=c.Config.single_user_login)))
        context.write(u'</td>\n</tr>\n</table>\n<p/>\n')
        # SOURCE LINE 93
        context.write(unicode(h.submit('Persist')))
        context.write(u'\n')
        # SOURCE LINE 94
        context.write(unicode(h.end_form))
        context.write(u'\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


