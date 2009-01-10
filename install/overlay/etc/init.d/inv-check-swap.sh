#! /bin/sh -e
#### BEGIN INIT INFO
# Provides:          inv-check-swap
# Default-Start:     
# Default-Stop:      
# Short-Description: makes sure the swap partition is ok
# Description:       makes sure the swap partition is ok
### END INIT INFO
#
# Author:	Jeff Wishnie <jeff@inveneo.org>
#
set -e

. /lib/lsb/init-functions

do_start () {
    log_daemon_msg "Checking swap..."
    /opt/inveneo/sbin/inv-check-swap.py 2>/dev/null
}

case "$1" in
    start|restart)
    do_start
    ;;
    stop)
	# No-op
    ;;
    *)
    echo "Usage: inv-check-swap.sh [start|stop]" >&2
    exit 3
    ;;
esac

exit 0
