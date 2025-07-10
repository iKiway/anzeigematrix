#!/bin/bash

# Anzeigematrix setup Matrix

echo "Setting up Anzeigematrix..."

# import necessary functions
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python3 and try again."
    exit 1
fi
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 and try again."
    exit 1
fi
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git and try again."
    exit 1
fi

# install pip
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip -y

# import necessary python libraries
sudo pip install git+https://github.com/iKiway/db_api.git --break-system-packages
sudo pip install pillow --break-system-packages
sudo pip install PRi.GPIO --break-system-packages


sudo apt install cython3 -y

cd
git clone https://github.com/hzeller/rpi-rgb-led-matrix
cd rpi-rgb-led-matrix
sudo apt install python3-dev python3-pillow -y
make build-python PYTHON=python3
echo "Starting the installation"
sudo make install-python PYTHON=python3

# blacklist snd_bcm28835
cd /etc/modprobe.d
echo 'blacklist snd_bcm2835' | sudo tee -a alsa-blacklist.conf

# turn off the build in sound module
cd /boot
sudo cp config.txt config_backup.txt
sudo sed -i 's/dtparam=audio=on/dtparam=audio=off/g' config.txt

# add isolopus=3 to remove flicker
sudo sed -i "s/$/ isolcpus=3/" "/boot/firmware/cmdline.txt"

########## Server Setup ##########
sudo pip install flask --break-system-packages
sudo pip install watchdog --break-system-packages

