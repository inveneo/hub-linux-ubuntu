#!/bin/bash

# work in /tmp
cd /tmp

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

# make inveeno user/group
echo "removing 'inveneo' user and group if they exist"
userdel -r inveneo 2>/dev/null
groupdel inveneo 2>/dev/null

echo "adding new 'inveneo' user/group"
groupadd -g 1400 inveneo
useradd -s /bin/bash -d /home/inveneo -g inveneo -u 1400 -p $PWD inveneo
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
usermod -aG netdev inveneo
usermod -aG admin inveneo
usermod -aG powerdev inveneo

# download and install Inveneo GPG key
echo "Installing Inveneo GPG key"
wget http://community.inveneo.org/apt/inveneo.gpg
apt-key add inveneo.gpg

# comment out cdrom in sources list
sed s/^deb\ cdrom/\#deb\ cdrom/ < /etc/apt/sources.list > /etc/apt/sources.list.new
mv /etc/apt/sources.list /etc/apt/sources.list~
mv /etc/apt/sources.list.new /etc/apt/sources.list

echo "Cleaning package cache"
apt-get clean

echo "Updating package list"
apt-get update

echo "installing Subversion and Ruby"
apt-get -y install subversion ruby rdoc

if [ $? -ne 0 ]
then
	echo "Failed to install SVN and Ruby. Cannot continue"
	exit -1
fi

echo "installing Rubygems"
wget -O rubygems.tar.gz http://rubyforge.org/frs/download.php/20989/rubygems-0.9.4.tgz
tar -xvzf rubygems.tar.gz
cd rubygems-*/
ruby setup.rb

if [ $? -ne 0 ]
then
        echo "Could not install rubygems"
        exit -1
fi 

gem update --system

cd /tmp

echo "checking out /opt/inveneo"
svn co http://svn.inveneo.org/repos/hub-linux-ubuntu/trunk/opt_inveneo /opt/inveneo

echo "checking out /opt/install"
svn co http://svn.inveneo.org/repos/hub-linux-ubuntu/trunk/install /opt/install

echo "generating /etc/iftab"
/opt/install/bin/geniftab.sh

echo "installing /etc/network/interfaces"
cp -a /opt/install/overlay/etc/network/interfaces /etc/network/interfaces

exit 0 
