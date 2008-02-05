<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
    <head>
        <title>Inveneo Configuration Server</title>
        ${h.stylesheet_link_tag('/screen.css')}

        <script type="text/javascript">
        function confirmSubmit() {
        var agree = confirm("Are you sure you wish to continue?");
        if (agree)
            return true;
        else
            return false;
        }
        </script>
    </head>

    <body>
        <table width="100%">
            <tr>
                <td align="left" width="50%">
                    <font size='+2'>Inveneo Configuration Server</font>
                </td>
                <td align="right">
                    %if 'admin' in session.keys() and session['admin']:
                    ${h.link_to('Sign Out',
                        url=h.url(controller='signin', action='signout'))}
                    <span class="small">(${session['admin']})</span>
                    %endif
                </td>
            </tr>
        </table>
        <hr>
        <div class="content">
        ${next.body()}\
        </div>
    </body>
</html>
