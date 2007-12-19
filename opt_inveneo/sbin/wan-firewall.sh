#!/bin/bash

# set a reasonable path
PATH=/bin:/sbin:/usr/bin:/usr/sbin

BLOCK_PORTS="10000 8008"
IFACE="eth0"

do_wall_up() {
    # Nat
    iptables -t nat -A POSTROUTING -o $IFACE -j MASQUERADE
    
    # Blocked ports
    for PORT in $BLOCK_PORTS 
    do
	iptables -A INPUT -i $IFACE -p tcp -m tcp --dport $PORT -j DROP 
    done
}

do_wall_down() {
    # NAT
    iptables -t nat -D POSTROUTING -o $IFACE -j MASQUERADE
    
    # Blocked ports
    for PORT in $BLOCK_PORTS
    do
	iptables -D INPUT -i $IFACE -p tcp -m tcp --dport $PORT -j DROP
    done
}

case "$1" in
    up)
	do_wall_up
	;;
    down)
	do_wall_down
	;;
    *)
	echo "Usage: wan-firewall.sh {up|down}"
	exit 3
	;;
esac

exit 0