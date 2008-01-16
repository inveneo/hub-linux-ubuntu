<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
    <head>
        <title>Inveneo Configuration Server</title>
        ${h.stylesheet_link_tag('/quick.css')}
        ${h.javascript_include_tag('/javascripts/effects.js', builtins=True)}
    </head>
    <body>
        <img src="/inveneo.png"><br/>
        <div class="content">
        ${next.body()}\
        </div>
    </body>
</html>
