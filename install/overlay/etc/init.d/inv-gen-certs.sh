#! /bin/sh -e
#### BEGIN INIT INFO
# Provides:          inv-gen-certs
# Default-Start:     
# Default-Stop:      
# Short-Description: generates hub self-signed certs for ssl
# Description:       generates hub self-signed certs for ssl
### END INIT INFO
#
# Author:	Jeff Wishnie <jeff@inveneo.org>
#
set -e

. /lib/lsb/init-functions

. /opt/inveneo/lib/bash/constants.sh

do_start () {
    log_daemon_msg "Generating certs and priv key if needed"
    if [ -d "$INV_HUB_CERTS_PATH" ]
    then
	log_daemon_msg "Certs dir '$INV_HUB_CERTS_PATH' found, doing nothing"
    else
	/opt/inveneo/sbin/inv-install-local-cert.py 2> /dev/null
    fi
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
