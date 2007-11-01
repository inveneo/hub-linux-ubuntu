#! /bin/sh -e
#### BEGIN INIT INFO
# Provides:          reconstruct-mirror
# Default-Start:     
# Default-Stop:      
# Short-Description: looks for new drives to fix degraded RAID1 arrays
# Description:       looks for new drives to fix degraded RAID1 arrays
### END INIT INFO
#
# Author:	Jeff Wishnie <jeff@inveneo.org>
#
set -e

. /lib/lsb/init-functions

do_start () {
    log_daemon_msg "Checking for RAID1 mirror reconstruct"
    /opt/inveneo/sbin/inv-rebuild-mirror.py
}

case "$1" in
    start|restart)
    do_start
    ;;
    stop)
	# No-op
    ;;
    *)
    echo "Usage: samba-shares.sh [start|stop]" >&2
    exit 3
    ;;
esac

exit 0
