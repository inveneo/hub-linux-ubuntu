#!/bin/sh

part_exists() {
    part=${1##/*/}
    drive=`expr "${part}" : '\([a-z]*\)'`
    [ -e /sys/block/$drive/$part ]
}


# args are: array-device device1 device2
# e.g. check_raid /dev/md0 /dev/sdb1 /dev/sdb2
check_raid() { 
    # try to examine superbock
    mdadm -E $1 2> /dev/null

    if [ $? -eq 0 ]
	then 
	echo "RAID at $1: OK"
    else
	# superblock is gone. Check if drives in array exist
	if  part_exists $2 
	    then
	    DRIVE1=$2
	else
	    DRIVE1="missing"
	fi
	if  part_exists $3 
	    then
	    DRIVE2=$3
	else
	    DRIVE2="missing"
	fi
	
	echo "Attempting to rewrite super-blocks for DEVICES: $DRIVE1,$DRIVE2 on ARRAY: $1"
	mdadm --create $1 --level=1 --raid-devices=2 --auto=yes  $DRIVE1 $DRIVE2
    fi
}


# Parse mdadmn.conf and rewrite superblocks if necessary
# arg is location of conf. e.g. check_suprblocks /etc/mdadm/mdadm.conf

if [ $# -eq 0 ]
then
    CONF=/etc/mdadm/mdadm.conf
else
    CONF=$1
fi

if [ ! -e $CONF ]
then
    echo "Conf file: \"$CONF\" not found"
    exit 1
fi

awk '/^ARRAY/ { 
    printf("%s ", $2) 
    for (i = 2; i <= NF; i++) 
    if ( split($i, devices_arg,"=") > 0 && 
	    devices_arg[1] == "devices" ) { 
	    num_devs = split(devices_arg[2], devices, ",") 
	    for ( j = 1; j <= num_devs; j++ ) { 
		printf("%s ", devices[j]) 
	    } 
	} 
	printf("\n") 
} ' $CONF | while read line; do
    check_raid $line
done









