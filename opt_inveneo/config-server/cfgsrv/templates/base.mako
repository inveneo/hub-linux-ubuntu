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
        <img src="/inveneo.png"><br/>
        %if 'admin' in session.keys() and session['admin']:
        ${h.link_to('Signout',
            url=h.url(controller='signin', action='signout'))}
        <span class="small">(${session['admin']})</span>
        %endif
        <div class="content">
        ${next.body()}\
        </div>
    </body>
</html>
