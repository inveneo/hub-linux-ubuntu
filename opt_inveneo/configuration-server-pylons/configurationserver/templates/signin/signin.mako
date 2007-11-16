<%include file="../header.mako"/>
<h3>Login</h3>
${h.form(h.url(controller='signin', action='signin_process'), method='post')}
% if c.Error and c.Error.has_key('signin'):
<b>${c.Error['signin']}<b>
<p/>
% endif
<table>
<tr>
<td>Username:</td>
<td>${h.text_field('username')}</td>
</tr>
<tr>
<td>Password:</td>
<td>${h.password_field('password')}</td>
</tr>
</table>
<p/>
${h.submit('Login')}
${h.end_form()}
