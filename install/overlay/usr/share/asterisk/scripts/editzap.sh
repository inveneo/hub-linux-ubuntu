#!/bin/bash

####################################################################
####	Copyright Brandon Kruse <bkruse@digium.com> && Digium	####
####################################################################

# Quick script for applying zaptel settings from the GUI.

ZAPCONF="/etc/zaptel.conf"
ZAPATACONF="/etc/asterisk/zapata.conf"
ZTCFG_OUTPUT="/var/lib/asterisk/static-http/config/ztcfg_output.html"
FILENAME="/etc/asterisk/applyzap.conf"
MISDNCONF="/etc/misdn-init.conf"
MISDNFILE="/etc/asterisk/applymisdn.conf"

case ${1} in
	changemodes)
		type=${2}
		$(for i in `lsmod | grep zap| sed 's/,/ /g'`; do rmmod $i >> /dev/null; done; rmmod zaptel) 
		case ${type} in
			e1)
				t1e1override=0
				$(modprobe zaptel; modprobe zttranscode; modprobe wct4xxp t1e1override=0; modprobe wcte11xp t1e1override=0; modprobe wct1xxp t1e1override=0; ztcfg)
			;;
			t1)
				t1e1override=1		
				$(modprobe zaptel; modprobe zttranscode; modprobe wct4xxp t1e1override=1; modprobe wcte11xp t1e1override=1; modprobe wct1xxp t1e1override=1; ztcfg)
			;;
			*)
				error_out "No mode to change specified"
			;;
		esac	
		;;
	applysettings)	
		# Split based on ||| delimeter, and apply to zaptel.
		if [ "${2}" == "misdn" ]
		then
			grep -v "\[general\]" ${MISDNFILE} | grep -v "\;" > ${MISDNCONF}
		else
			grep -v "\[general\]" ${FILENAME} | grep -v "\;" > ${ZAPCONF} 
			cp -rf ${ZAPCONF} ${ZAPCONF}.zapscan # save the gui settings!
			cp -rf ${ZAPATACONF} ${ZAPATACONF}.zapscan # save the user settings
			zapscan
		fi
		;;
	ztcfg)
		ztcfg -vv 2> $ZTCFG_OUTPUT
		;;
esac

function error_out() {
	echo "${1}" > ${ZTCFG_OUTPUT}
}
