#! /bin/sh -e
#### BEGIN INIT INFO
# Provides:          samba-shares
# Default-Start:     2 3 4 5
# Default-Stop:      S 0 1 6
# Short-Description: generates /etc/inveneo/samba/shares.conf 
# Description:       generates /etc/inveneo/samba/shares.conf 
#                    by reading all *.conf files in /etc/inceneo/samba/shares.d
### END INIT INFO
#
# Author:	Jeff Wishnie <jeff@inveneo.org>
#
set -e

PATH=/bin:/usr/bin:/sbin:/usr/sbin

INV_SAMBA_CONF_D=/etc/inveneo/samba
SHARES_D=${INV_SAMBA_CONF_D}/shares.d
SHARES_CONF=${INV_SAMBA_CONF_D}/shares.conf

HEADER="# ========= DO NOT EDIT: GENERATED AT BOOT TIME FROM CONTENTS OF shares.d"

. /lib/lsb/init-functions

do_start () {
    echo ${HEADER} > ${SHARES_CONF}
    
    if [ -d "${SHARES_D}" ]
	then
	for f in "${SHARES_D}"/*
	  do
	  echo "include = $f" >> "${SHARES_CONF}"
	done
    fi
}

case "$1" in
    start)
    do_start
    ;;
    restart|reload|force-reload)
    echo "Error: argument '$1' not supported" >&2
    exit 3
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
