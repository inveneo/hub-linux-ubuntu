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

INCLUDE_D=/etc/inveneo/samba
INCLUDE_FILE=${INCLUDE_D}/shares.conf
SAMBA_SHARES_D=${INCLUDE_D}/shares.d

HEADER="# ========= DO NOT EDIT: GENERATED AT BOOT TIME FROM CONTENTS OF ${SAMBA_SHARES_D}"

. /lib/lsb/init-functions

do_start () {
    mkdir -p "${INCLUDE_D}"

    echo ${HEADER} > "${INCLUDE_FILE}"
    
    if [ -d "${SAMBA_SHARES_D}" ]
	then
	find "${SAMBA_SHARES_D}" -name "*.conf" | while read f
	  do
	  echo "include = $f" >> "${INCLUDE_FILE}"
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
