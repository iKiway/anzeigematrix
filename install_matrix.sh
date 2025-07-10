#!bin/bash

# blacklist snd_bcm28835
cd /etc/modprobe.d
echo 'blacklist snd_bcm2835' | sudo tee -a alsa-blacklist.conf


# turn off the build in sound module
cd /boot
sudo cp config.txt config_backup.txt
sudo sed -i 's/dtparam=audio=on/dtparam=audio=off/g' config.txt

# add isolopus=3 to remove flicker
sudo sed -i "s/$/ isolcpus=3/" "/boot/cmdline.txt"

# install packages
sudo pip install pyhafas
sudo pip install pillow
sudo pip install PRi.GPIO

# clone libary rpi-rgb-led-matrix
cd
git clone https://github.com/hzeller/rpi-rgb-led-matrix

# install libary rpi-rgb-led-matrix
cd rpi-rgb-led-matrix
sudo apt update
sudo apt install python3-dev python3-pillow -y
make build-python PYTHON=python3
echo "start the installation"
sudo make install-python PYTHON=python3
echo "rebooting now"
