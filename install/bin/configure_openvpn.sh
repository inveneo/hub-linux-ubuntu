#!/bin/bash

#
# Automatically configure openvpn and build keys
#

source /etc/openvpn/easy-rsa/vars
/etc/openvpn/easy-rsa/clean-all
/etc/openvpn/easy-rsa/build-dh
#/etc/openvpn/easy-rsa/pkitool --csr HOSTNAME

