# A decent PATH
PATH=/bin:/sbin:/usr/bin:/usr/sbin

# source shared constants
. /opt/inveneo/lib/bash/constants.sh

# Inveneo variables

INV_TRUE=0 # to match bash's 'test' and '[' constructs
INV_FALSE=1

# Drive partitions
INV_ROOT_DRIVE=`rdev | awk -F '/' '{ print "/"$(NF-2)"/"substr($(NF-1),0,match($(NF-1),/[0-9]+.*$/)) }'`

# network
PRIMARY_ENET=`ifconfig -a | awk '/HWaddr/ { print $5; exit }' | sed s/://g | tr '[:upper:]' '[:lower:]'`

# Boot flags
INSTALL_MODE_REQUESTED_FLAG=${INV_BOOT_FLAG_DIR}/${INV_BOOT_FLAG_REQUEST_INSTALL_MODE}
INSTALL_MODE_ACTIVE_FLAG=${INV_BOOT_FLAG_DIR}/${INV_BOOT_FLAG_INSTALL_MODE_ACTIVE}
FACTORY_MODE_REQUESTED_FLAG=${INV_BOOT_FLAG_DIR}/${INV_BOOT_FLAG_REQUEST_FACTORY_MODE}
FACTORY_MODE_ACTIVE_FLAG=${INV_BOOT_FLAG_DIR}/${INV_BOOT_FLAG_FACTORY_MODE_ACTIVE}

# install mode
if [ -f $INSTALL_MODE_REQUESTED_FLAG ]
    then
    INSTALL_MODE_REQUESTED=$INV_TRUE
    else
    INSTALL_MODE_REQUESTED=$INV_FALSE
fi

if [ -f $INSTALL_MODE_ACTIVE_FLAG ]
    then
    INSTALL_MODE_ACTIVE=$INV_TRUE
    else
    INSTALL_MODE_ACTIVE=$INV_FALSE
fi

# factory mode
if [ -f $FACTORY_MODE_REQUESTED_FLAG ]
    then
    FACTORY_MODE_REQUESTED=$INV_TRUE
    else
    FACTORY_MODE_REQUESTED=$INV_FALSE
fi

if [ -f $FACTORY_MODE_ACTIVE_FLAG ]
    then
    FACTORY_MODE_ACTIVE=$INV_TRUE
    else
    FACTORY_MODE_ACTIVE=$INV_FALSE
fi
