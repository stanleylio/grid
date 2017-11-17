#!/bin/bash

DIR="/home/grid/backup"

if ! [ -e "$DIR" ]
then
	mkdir $DIR
fi

sudo rsync -aH --chmod=ugo=rX --delete /etc/apache2 $DIR
sudo rsync -aH --chmod=ugo=rX --delete /etc/supervisor $DIR
sudo rsync -aH --chmod=ugo=rX --delete /etc/logrotate.d $DIR
sudo rsync -aH --chmod=ugo=rX --delete /etc/rsnapshot $DIR
sudo rsync -aH --chmod=ugo=rX --delete /etc/cron.d $DIR
sudo rsync -aH --chmod=ugo=rX --delete /etc/rabbitmq $DIR
sudo rsync -aH --chmod=ugo=rX --delete /var/lib/connman $DIR
sudo rsync -aH --chmod=ugo=rX --delete /etc/wpa_supplicant $DIR

crontab -l > $DIR/crontab.txt
cp /etc/fstab $DIR/fstab
if [ -a /boot/uEnv.txt ]
then
	cp /boot/uEnv.txt $DIR/uEnv.txt
fi
cp -a /etc/network/interfaces $DIR/interfaces.txt
cp -a /etc/hostname $DIR/hostname.txt
cp -a /etc/hosts $DIR/hosts.txt
#cp -a /etc/resolv.conf $DIR/resolv.conf.txt
cat /etc/resolv.conf > $DIR/resolv.conf.txt
cp -a /etc/rc.local $DIR/rc.local.txt
cp -a /etc/ntp.conf $DIR/ntp.conf
