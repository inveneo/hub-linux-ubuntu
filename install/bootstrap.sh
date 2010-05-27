#!/bin/bash

# SVN Report
REPO="http://svn.inveneo.org/repos/hub-linux-ubuntu/branches/ihl-2.0"

# work in /tmp
cd /tmp

# Pwd for root
PWD='$1$9dREJf0D$q79s8EjHbvxEWYeWXc4RT/'

# Set root pwd
echo "Resetting root password"
usermod -p $PWD root

# add 'inveneo' user

# create 'permission' groups for users
echo "Creating extra 'permissions' groups"
groupadd -g  200 lpadmin 2>/dev/null || groupmod -g 200 lpadmin
groupadd -g  201 scanner 2>/dev/null || groupmod -g 201 scanner
groupadd -g  202 fuse 2>/dev/null || groupmod -g 202 fuse
groupadd -g  203 inveneo_users 2>/dev/null || groupmod -g 203 inveneo_users

# make inveeno user/group
echo "removing 'inveneo' user and group if they exist"
userdel -fr inveneo 2>/dev/null
groupdel inveneo 2>/dev/null

echo "adding new 'inveneo' user/group"
groupadd -g 1400 inveneo
useradd -s /bin/bash -m -d /home/inveneo -g inveneo -u 1400 -p $PWD inveneo
echo "adding 'inveneo' to permissions groups, one at a time in case any fail"
usermod -aG adm inveneo
usermod -aG dialout inveneo
usermod -aG fax inveneo
usermod -aG voice inveneo
usermod -aG cdrom inveneo
usermod -aG floppy inveneo
usermod -aG audio inveneo
usermod -aG dip inveneo
usermod -aG video inveneo
usermod -aG plugdev inveneo
usermod -aG games inveneo
usermod -aG lpadmin inveneo
usermod -aG scanner inveneo
usermod -aG fuse inveneo
#usermod -aG netdev inveneo
#usermod -aG powerdev inveneo
usermod -aG admin inveneo

# download and install Inveneo GPG key
echo "Installing Inveneo GPG key"
wget http://community.inveneo.org/certs/inveneo.gpg
apt-key add inveneo.gpg

# comment out cdrom in sources list
sed s/^deb\ cdrom/\#deb\ cdrom/ < /etc/apt/sources.list > /etc/apt/sources.list.new
mv /etc/apt/sources.list /etc/apt/sources.list~
mv /etc/apt/sources.list.new /etc/apt/sources.list

echo "installing Subversion"
apt-get -y install subversion

if [ $? -ne 0 ]
then
	echo "Failed to install SVN. Cannot continue"
	exit -1
fi

cd /tmp

echo "checking out /opt/inveneo"
svn co $REPO/opt_inveneo /opt/inveneo

echo "checking out /opt/install"
svn co $REPO/install /opt/install

echo "copying in APT settings"
cp -a /opt/install/overlay/etc/apt /etc

echo "updating packages"
apt-get update
apt-get -y --force-yes dist-upgrade
apt-get autoremove -y --force-yes
apt-get clean -y --force-yes

echo "installing /etc/network/interfaces"
cp -a /opt/install/overlay/etc/network/interfaces /etc/network/interfaces

echo "Restart required (really, you gotta). Hit enter/return to do reboot"
read -n 1 char
reboot
exit 0 
