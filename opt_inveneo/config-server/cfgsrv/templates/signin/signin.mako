<%inherit file="/base.mako"/>

<h3 class="header">Configuration Server Login</h3>
${h.form(h.url(controller='signin', action='signin_process'), method='post')}
% if c.Error and c.Error.has_key('signin'):
<p class="error">${c.Error['signin']}</p>
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
<br>
${h.submit('Login')}
${h.end_form()}
