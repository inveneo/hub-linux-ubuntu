#!/bin/bash

####################################################################
####	Copyright Brandon Kruse <bkruse@digium.com> && Digium	####
####################################################################

#### Props and Credits to the m0n0wall and the xwrt group for information.
#### Extra licensing information included in the svg files located at
#### /var/lib/asterisk/static-http/config/graphs/*.svg. Thanks Guys!

echo `date`
case $1 in
	cpu)
		var="`head -n 1 /proc/stat`"
		echo "$var"
		;;
	wan)
		var="`cat /proc/net/dev | grep eth0`"
		echo "$var"
		;;
	lan) 
		var="`cat /proc/net/dev | grep eth1`"
		echo "$var"
		;;
	hd)
		var="`df -h`"	
		echo "$var"
		;;
	mem)
		var="`free`"
		echo "$var"
		;;
	temp)
		var="`echo \"temperature sensor?\"`"
		echo "$var"
		;;
	ast)
		var="`asterisk -rx 'core show channels'`"
		echo "$var"
		;;
	swap)
		SWAPINFO=$(free | grep "Swap:")
		nI="0"
		for CUR_VAR in $SWAPINFO; do
			case "$nI" in
				1)	TOTAL_SWAP=$CUR_VAR;;
				3)	FREE_SWAP=$CUR_VAR
			break;;
			esac
		let "nI+=1"
		done
		;;
	
esac
#/proc/net/dev
