#! /bin/sh -e
#### BEGIN INIT INFO
# Provides:          inv-id-md-drives
# Default-Start:     
# Default-Stop:      
# Short-Description: id's drives and records serial numbers
# Description:       id's drives and records serial numbers
### END INIT INFO
#
# Author:	Jeff Wishnie <jeff@inveneo.org>
#
set -e

. /lib/lsb/init-functions

do_start () {
    log_daemon_msg "Recording drive serial numbers (if 2 drives found)"
    /opt/inveneo/sbin/inv-id-md-drives.py /dev/md0
}

case "$1" in
    start|restart)
    do_start
    ;;
    stop)
	# No-op
    ;;
    *)
    echo "Usage: inv-id-md-drives.sh [start|stop]" >&2
    exit 3
    ;;
esac

exit 0
