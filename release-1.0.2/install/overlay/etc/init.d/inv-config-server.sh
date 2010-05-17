#! /bin/sh
#### BEGIN INIT INFO
# Provides:          inv-config-server
# Default-Start:     2 3 4 5
# Default-Stop:      S 0 1 6
# Short-Description: starts/stops station configuarion server
# Description:       
### END INIT INFO
#
# Author:	Jeff Wishnie <jeff@inveneo.org>
#

PATH=/bin:/usr/bin:/sbin:/usr/sbin

SERVER_DIR='/opt/inveneo/config-server'

. /lib/lsb/init-functions

do_start () {
    log_daemon_msg "Starting Inveneo Configuration Server"
    cd ${SERVER_DIR}
    /usr/bin/paster serve --daemon development.ini start
}

do_stop () {
    log_daemon_msg "Stopping Inveneo Configuration Server"
    cd ${SERVER_DIR}
    /usr/bin/paster serve development.ini stop
}

case "$1" in
    start)
    do_start
    ;;
    restart|reload|force-reload)
    do_stop
    do_start
    ;;
    stop)
    do_stop
    ;;
    *)
    echo "Usage: inv-config-server.sh [start|stop|restart]" >&2
    exit 3
    ;;
esac

exit 0
