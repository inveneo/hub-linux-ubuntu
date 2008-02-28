#  Created by Jeff Wishnie on 2007-05-24.
#  Copyright (c) 2007. All rights reserved.

INV_OS_VERSION_FILE="/etc/inveneo/os_version"
INV_LOCAL_CONFIG_FILE_DIR="/etc/inveneo/conf.d"
INV_LOCAL_USER_CONFIG_DIR="/mnt/rw/users"
INV_LOCAL_MACHINE_CONFIG_DIR="/mnt/rw/config"
INV_LOCAL_MACHINE_CONFIG_FILE="/mnt/rw/config/station.tar.gz"
INV_LOCAL_MACHINE_INITIAL_CONFIG_FILE="/mnt/rw/config/initial-config.conf"
INV_LOCAL_NET_CONFIG_FILE="/mnt/rw/config/station-net.tar.gz"
INV_LOCAL_NET_FACTORY_CONFIG_FILE="/opt/inveneo/config/station-net-factory.tar.gz"
INV_USER_SKELETON="/opt/inveneo/skeleton/user"
INV_LOG="/var/log/inveneo.log"
INV_TAR_FLAGS="--preserve --same-owner --atime-preserve --exclude=.svn --totals"
INV_USER_SAVE_DATA_DESC="/opt/inveneo/config/user-save-data.conf"
INV_SYSTEM_SAVE_DATA_DESC="/opt/inveneo/config/system-save-data.conf"
INV_NET_SAVE_DATA_DESC="/opt/inveneo/config/net-save-data.conf"
INV_SAVED_DATA_FILE_POSTFIX="tar.gz"
INV_BOOT_FLAG_DIR="/mnt/rw/flags"
INV_BOOT_FLAG_REQUEST_INSTALL_MODE="install_mode"
INV_BOOT_FLAG_INSTALL_MODE_ACTIVE="install_mode_active"
INV_BOOT_FLAG_REQUEST_FACTORY_MODE="factory_mode"
INV_BOOT_FLAG_FACTORY_MODE_ACTIVE="factory_mode_active"
INV_HUB_CONF_FILE="hub.conf"
INV_STATION_CONF_FILE="station.conf"
INV_CONFIG_SERVICE_NAME="_inv-stat-conf._tcp"
INV_CONFIG_SERVICE_URI="/configuration"
INV_CONFIG_SERVICE_GET_STATION_INITIAL_CONFIG_COMMAND="get_station_initial_config"
INV_CONFIG_SERVICE_GET_STATION_CONFIG_COMMAND="get_station_config"
INV_CONFIG_SERVICE_SAVE_STATION_INITIAL_CONFIG_COMMAND="save_station_initial_config"
INV_CONFIG_SERVICE_SAVE_STATION_CONFIG_COMMAND="save_station_config"
INV_CONFIG_SERVICE_GET_USER_CONFIG_COMMAND="get_user_config"
INV_CONFIG_SERVICE_SAVE_USER_CONFIG_COMMAND="save_user_config"
INV_CONFIG_SERVICE_GET_VERSION_COMMAND="version"

# Constants for use on server
INV_MONITOR_BEEP_ALERT='beep -f 1000 -n -f 1200 -n -f 1500 -n -f 1700 -n -f 1950 -n -f 2200 -n -f 2400 -n -f 2700'

INV_MONITOR_SMTP_USERNAME='inveneo.smtp@gmail.com'
INV_MONITOR_SMTP_PASSWORD='1qaz2wsx'
INV_MONITOR_SMTP_HOSTNAME='smtp.gmail.com'
INV_MONITOR_SMTP_PORT=587
INV_MONITOR_SMTP_TLS=1
INV_MONITOR_SMTP_SENDER='inveneo.smtp@gmail.com'
INV_MONITOR_SMTP_DEFAULT_MESSAGE="Host has a failed disk drive:"
INV_MONITOR_SMTP_DEFAULT_SUBJECT="Subject: CRITICAL PROBLEM: A hard disk has failed"

# If you have email notifications, we recommend you change the sleep to 720 minutes (12 hours)
INV_MONITOR_DEGRADE_ACTIONS_SLEEP_MINUTES=30

# You must provide an email address for email notifications to work
INV_MONITOR_SMTP_RECIPIENT=''
