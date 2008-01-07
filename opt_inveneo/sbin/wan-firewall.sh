#!/bin/bash

# set a reasonable path
PATH=/bin:/sbin:/usr/bin:/usr/sbin

# default ports to block on wan interface are:
# 80 (http)
# 443 (https)
# 10000 (webmin)
# 8008 (inveneo configuration server)
# 8088 (asterisk configuration)
# 631 (cups and cups admin)
# 3128 (squid web proxy)
# 389 (ldap)
# 53 (dns)
# 5353 (mDns)

BLOCK_PORTS="80 443 10000 8008 8088 631 3128 389 53 5353"
IFACE="eth0"

do_wall_up() {
    # Nat
    iptables -t nat -A POSTROUTING -o $IFACE -j MASQUERADE
    
    # Blocked ports
    for PORT in $BLOCK_PORTS 
    do
	iptables -A INPUT -i $IFACE -p tcp --dport $PORT -j DROP 
	iptables -A INPUT -i $IFACE -p udp --dport $PORT -j DROP 
    done
}

do_wall_down() {
    # NAT
    iptables -t nat -D POSTROUTING -o $IFACE -j MASQUERADE
    
    # Blocked ports
    for PORT in $BLOCK_PORTS
    do
	iptables -D INPUT -i $IFACE -p tcp --dport $PORT -j DROP
	iptables -D INPUT -i $IFACE -p udp --dport $PORT -j DROP
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