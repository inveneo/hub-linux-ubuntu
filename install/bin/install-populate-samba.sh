#!/bin/sh

#shut down samba
	echo -n "shutting down samba....."
	/etc/init.d/samba stop
	echo "   done."

#shut down slapd
	echo -n "shutting down slapd...."
	/etc/init.d/slapd stop
	echo "    done."


#start up slapd
	echo -n "starting slapd with new config..."
	/etc/init.d/slapd start
	echo "    done."

#execute samba db population
	smbpasswd -w 1nvene0
	/usr/sbin/smbldap-populate -u 10000 -g 10000
	/opt/inveneo/bin/smbldap-migrate-unix-groups -G /etc/group

#start up samba
	echo -n "starting samba with new config..."
	/etc/init.d/samba start
	echo "    done."


