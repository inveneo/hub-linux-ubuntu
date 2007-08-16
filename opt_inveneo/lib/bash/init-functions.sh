# Inveneo Initialization functions and variables
PATH=/bin:/sbin:/usr/bin

# source shared constants
. /opt/inveneo/lib/bash/constants.sh

set_boot_flag() {
    touch $1
}

clear_boot_flag() {
    rm $1
}

# args are <root_dir> <archive_file>
restore_config_data() {
    tar -C $1 $INV_TAR_FLAGS -xvzf $2
}