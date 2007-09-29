#!/bin/sh

# set a reasonable path
PATH=/bin:/sbin:/usr/bin:/usr/sbin

part_exists() {
    part=${1##/*/}
    drive=`expr "${part}" : '\([a-z]*\)'`

    if [ -e /sys/block/$drive/$part ]
	then
	return 0
    else
	echo "Can't find $part, trying to forcing a partprobe"
	partprobe /dev/$drive
	[ -e /sys/block/$drive/$part ]
    fi
}


# args are: array-device device1 device2
# e.g. check_raid /dev/md0 /dev/sdb1 /dev/sdb2
check_raid() { 
    if mdadm --detail --brief --test $1
	then
	echo "RAID array at $1 already active"
	return
    fi

    # try to examine superblocks
    mdadm -E $2 2> /dev/null
    DRIVE1_SUPERBLOCK_OK=$?

    mdadm -E $3 2> /dev/null
    DRIVE2_SUPERBLOCK_OK=$?

    if  [ $DRIVE1_SUPERBLOCK_OK -eq 0 ] &&  [ $DRIVE2_SUPERBLOCK_OK -eq 0 ]
	then 
	echo "RAID array at $1 has superblocks. Leaving along"
	return
    fi
    
    # superblock is gone. Check if drives in array exist
    if  part_exists $2 
	then
	DRIVE1=$2
    else
	echo "$2 not found, marking as 'missing'"
	DRIVE1="missing"
    fi
    if  part_exists $3 
	then
	DRIVE2=$3
    else
	echo "$3 not found, marking as 'missing'"
	DRIVE2="missing"
    fi
    
    # see if we have the drive present that has the problem to bother rewriting
    SHOULD_REWRITE=1 # false
    if [ ! $DRIVE1_SUPERBLOCK_OK -eq 0 ] && [ $DRIVE1 != "missing" ]
	then
	SHOULD_REWRITE=0
    elif [ ! $DRIVE2_SUPERBLOCK_OK -eq 0 ] && [ $DRIVE2 != "missing" ]
	then
	SHOULD_REWRITE=0
    fi
    
    if [ $SHOULD_REWRITE -eq 0 ]
	then
	echo "Attempting to rewrite super-blocks for DEVICES: $DRIVE1,$DRIVE2 on ARRAY: $1"
	yes | mdadm --create $1 --level=1 --raid-devices=2 --auto=yes  $DRIVE1 $DRIVE2
	if [ $? -eq 0 ]
	    then
	    echo "stopping newly created array"
	    mdadm --stop $1
	fi
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
	printf("\n") } ' $CONF | while read line; do
    check_raid $line
done

# always exit with success
exit 0








