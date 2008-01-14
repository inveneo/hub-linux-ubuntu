#!/bin/sh

# NOTE: Host, tunneluser and port must be changed for specific deploys

HOST=scooter.inveneo.org
TUNNELUSER=mvp-ug_tunnel
PORT=40000
CMD="ping -q -i 60 mvp-ug.inveneo.net"
# CMD="ping -q -i 60 www.yahoo.com"

TUNNELCOUNT=`ps ax | grep "$CMD" | grep -v grep | wc -l`

if [ $TUNNELCOUNT -eq 0 ]; then
        ssh -R $PORT:127.0.0.1:22 $TUNNELUSER@$HOST $CMD &
fi

