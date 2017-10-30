#/bin/bash

sudo adduser grid
sudo passwd grid
sudo chsh -s /bin/bash grid
sudo usermod -aG sudo grid
sudo usermod -aG i2c grid
sudo usermod -aG dialout grid
sudo visudo -f /etc/sudoers.d/grid
#grid ALL=(ALL) NOPASSWD:ALL

sudo nano /etc/hostname
sudo nano /etc/hosts

# change root password
sudo passwd
# remove default users
sudo deluser --remove-home pi
sudo deluser --remove-home fa


ssh-keygen
#cat ~/.ssh/id_rsa.pub

sudo apt update && sudo apt upgrade -y
sudo apt install git supervisor ntp ntpdate minicom autossh sqlite3 -y --force-yes
sudo apt autoremove

sudo systemctl enable supervisor
sudo systemctl start supervisor

cd
git clone https://github.com/stanleylio/grid
cd ~/grid
git config --global user.name "Stanley Lio"
git config --global user.email stanleylio@gmail.com
cd

sudo apt install build-essential python3-dev python3-setuptools python3-pip python3-twisted -y
sudo pip3 install pyserial requests pycrypto pika

cd
wget https://github.com/rabbitmq/rabbitmq-server/releases/download/rabbitmq_v3_6_12/rabbitmq-server_3.6.12-1_all.deb
sudo dpkg -i rabbitmq-server_3.6.12-1_all.deb
sudo apt -f install -y
sudo dpkg -i rabbitmq-server_3.6.12-1_all.deb
#sudo rabbitmqctl add_user $HOSTNAME password here
#sudo rabbitmqctl add_vhost grid
#sudo rabbitmqctl set_permissions $HOSTNAME -p grid ".*" ".*" ".*"
#sudo rabbitmqctl set_user_tags $HOSTNAME administrator
#sudo rabbitmqctl list_user_permissions $HOSTNAME
sudo rabbitmqctl delete_user guest
sudo rabbitmq-plugins enable rabbitmq_management
sudo rabbitmq-plugins enable rabbitmq_shovel
sudo rabbitmq-plugins enable rabbitmq_shovel_management
