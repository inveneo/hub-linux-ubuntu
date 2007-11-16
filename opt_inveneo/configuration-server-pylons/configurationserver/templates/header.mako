<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<head><title>Inveneo</title></head>
<img src="/inveneo.png" alt="inveneo">
%if 'user' in session.keys() and session['user']:
<%include file="breadcrumps.mako"/>
%endif


<script language="JavaScript">
function confirmSubmit()
{
var agree=confirm("Are you sure you wish to continue?");
if (agree)
	return true ;
else
	return false ;
}
</script>