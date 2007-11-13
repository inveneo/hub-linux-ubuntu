from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1194993370.2331059
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
        runtime._include_file(context, u'../header.html', _template_uri)
        context.write(u'\n<h3>Set Initial Configuration</h3>\n')
        # SOURCE LINE 3
        context.write(unicode(h.form(h.url(controller='admin', action='config_edit_process', id=c.Config.id), method='post')))
        context.write(u'\n<!-- ')
        # SOURCE LINE 4
        context.write(unicode(h.start_form('/admin/config_edit_process')))
        context.write(u' -->\n\n<table>\n<tr>\n<td>MAC:</td>\n<!-- the next line checks if mac is not set -- there must be a better way -->\n')
        # SOURCE LINE 10
        if not c.Edit:
            # SOURCE LINE 11
            context.write(u'     <td>')
            context.write(unicode(h.text_field('mac', value=c.Config.mac)))
            context.write(u'</td>\n')
            # SOURCE LINE 12
            if c.Error and c.Error.has_key('mac'):
                # SOURCE LINE 13
                context.write(u'       <td><b>')
                context.write(unicode(c.Error['mac']))
                context.write(u'<b></td>\n')
            # SOURCE LINE 15
        else:
            # SOURCE LINE 16
            context.write(u'<td>')
            context.write(unicode(c.Config.mac))
            context.write(u'</td>\n')
        # SOURCE LINE 18
        context.write(u'</tr>\n<tr>\n<td>Time Zone:</td>\n<td>\n')
        # SOURCE LINE 22
        context.write(unicode( h.select('timezone', h.options_for_select(h.get_timezones_as_string_list(), c.Config.timezone)) ))
        context.write(u'\n</td>\n</tr>\n<td>NTP On:</td>\n<td>')
        # SOURCE LINE 26
        context.write(unicode(h.check_box('ntp_on', checked=c.Config.ntp_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>NTP Servers:</td>\n<td>')
        # SOURCE LINE 30
        context.write(unicode(h.text_field('ntp_servers', value=c.Config.ntp_servers)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Proxy On:</td>\n<td>')
        # SOURCE LINE 34
        context.write(unicode(h.check_box('proxy_on', checked=c.Config.proxy_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTP Proxy:</td>\n<td>')
        # SOURCE LINE 38
        context.write(unicode(h.text_field('http_proxy', value=c.Config.http_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTP Proxy Port:</td>\n<td>')
        # SOURCE LINE 42
        context.write(unicode(h.text_field('http_proxy_port', value=c.Config.http_proxy_port)))
        context.write(u'</td>\n')
        # SOURCE LINE 43
        if c.Error and c.Error.has_key('http_proxy_port'):
            # SOURCE LINE 44
            context.write(u'     <td><b>')
            context.write(unicode(c.Error['http_proxy_port']))
            context.write(u'<b></td>\n')
        # SOURCE LINE 46
        context.write(u'</tr>\n<tr>\n<td>HTTPS Proxy:</td>\n<td>')
        # SOURCE LINE 49
        context.write(unicode(h.text_field('https_proxy', value=c.Config.https_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>HTTPS Proxy Port:</td>\n<td>')
        # SOURCE LINE 53
        context.write(unicode(h.text_field('https_proxy_port', value=c.Config.https_proxy_port)))
        context.write(u'</td>\n')
        # SOURCE LINE 54
        if c.Error and c.Error.has_key('https_proxy_port'):
            # SOURCE LINE 55
            context.write(u'     <td><b>')
            context.write(unicode(c.Error['https_proxy_port']))
            context.write(u'<b></td>\n')
        # SOURCE LINE 57
        context.write(u'</tr>\n<tr>\n<td>FTP Proxy:</td>\n<td>')
        # SOURCE LINE 60
        context.write(unicode(h.text_field('ftp_proxy', value=c.Config.ftp_proxy)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>FTP Proxy Port:</td>\n<td>')
        # SOURCE LINE 64
        context.write(unicode(h.text_field('ftp_proxy_port', value=c.Config.ftp_proxy_port)))
        context.write(u'</td>\n')
        # SOURCE LINE 65
        if c.Error and c.Error.has_key('ftp_proxy_port'):
            # SOURCE LINE 66
            context.write(u'     <td><b>')
            context.write(unicode(c.Error['ftp_proxy_port']))
            context.write(u'<b></td>\n')
        # SOURCE LINE 68
        context.write(u'</tr>\n<tr>\n<td>Phone Home On:</td>\n<td>')
        # SOURCE LINE 71
        context.write(unicode(h.check_box('phone_home_on', checked=c.Config.phone_home_on)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Phone Home Reg:</td>\n<td>')
        # SOURCE LINE 75
        context.write(unicode(h.text_field('phone_home_reg', value=c.Config.phone_home_reg)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Phone Home Checkin:</td>\n<td>')
        # SOURCE LINE 79
        context.write(unicode(h.text_field('phone_home_checkin', value=c.Config.phone_home_checkin)))
        context.write(u'</td>\n</tr>\n<tr>\n<td>Locale:</td>\n<td>')
        # SOURCE LINE 83
        context.write(unicode(h.text_field('locale', value=c.Config.locale)))
        context.write(u'</td>\n')
        # SOURCE LINE 84
        if c.Error and c.Error.has_key('locale'):
            # SOURCE LINE 85
            context.write(u'     <td><b>')
            context.write(unicode(c.Error['locale']))
            context.write(u'<b></td>\n')
        # SOURCE LINE 87
        context.write(u'</tr>\n<tr>\n<td>foo</td>\n<td>\n')
        # SOURCE LINE 91
        context.write(unicode( h.tag('select', open=True, name_='time_frame', id='time_frame') ))
        context.write(u'\n')
        # SOURCE LINE 92
        context.write(unicode( h.options_for_select(['', '1-3 months', '3-6 months', '6-9 months', '10+ months']) ))
        context.write(u'\n</td>\n</tr>\n<tr>\n<td>Single User Login:</td>\n<td>')
        # SOURCE LINE 97
        context.write(unicode(h.check_box('single_user_login', checked=c.Config.single_user_login)))
        context.write(u'</td>\n</tr>\n</table>\n</p>\n')
        # SOURCE LINE 101
        context.write(unicode(h.submit('Persist')))
        context.write(u'\n')
        # SOURCE LINE 102
        context.write(unicode(h.end_form))
        context.write(u'\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


