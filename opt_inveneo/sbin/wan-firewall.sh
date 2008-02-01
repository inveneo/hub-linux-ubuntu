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

do_wall_up() {
    IFACE=$1

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
    IFACE=$1

    # NAT
    iptables -t nat -D POSTROUTING -o $IFACE -j MASQUERADE
    
    # Blocked ports
    for PORT in $BLOCK_PORTS
    do
	iptables -D INPUT -i $IFACE -p tcp --dport $PORT -j DROP
	iptables -D INPUT -i $IFACE -p udp --dport $PORT -j DROP
    done
}

usage() {
    echo "Usage: $0 [iface] up|down"
    exit 3
}

default="eth0"
case "$1" in
    "") usage ;;
    "start" | "up") do_wall_up $default ;;
    "stop" | "down") do_wall_down $default ;;
    *)
    case "$2" in
        "") usage ;;
        "start" | "up") do_wall_up $1 ;;
        "stop" | "down") do_wall_down $1 ;;
        *) usage ;;
    esac
esac

exit 0
