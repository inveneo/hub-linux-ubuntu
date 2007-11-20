<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<head>
<link rel=stylesheet type="text/css" href="/screen.css" media=screen>
<title>Inveneo</title>
</head>
<table width="100%">
<tr>
<td><img src="/inveneo.png" alt="inveneo"></td>
<td valign="top" align="right">
%if 'admin' in session.keys() and session['admin']:
${h.link_to('Signout', url=h.url(controller='signin', action='signout'))}
<span class="small">(${session['admin']})</span>
%endif
</td>
</tr>
</table>

%if 'admin' in session.keys() and session['admin']:
<%include file="breadcrumps.mako"/>
%endif

<script type="text/javascript">
function confirmSubmit()
{
var agree=confirm("Are you sure you wish to continue?");
if (agree)
	return true ;
else
	return false ;
}
</script>
