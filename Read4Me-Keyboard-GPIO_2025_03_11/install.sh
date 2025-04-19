#!/bin/bash
# Install PiTextReader
# 
# Run using:
# $ sh install.sh
#
# Can be safely run multiple times
#
# version 20180210
#

if [ "$EUID" -ne 0 ]
  then echo "Must run as root: 'sudo ./install.sh'"
  exit
fi

# Make sure python requirements are installed
apt-get -y update
apt-get -y upgrade


echo  

# Install packages
sudo apt-get install -y tesseract-ocr tesseract-ocr-fra alsa-utils
sudo apt-get install -y python3-rpi.gpio python3-gpiozero 
sudo apt-get install mplayer -y


# Install python module required
#sudo pip3 install pytesseract opencv-python rpi_ws281x adafruit-circuitpython-neopixel
sudo python3 -m pip install --break-system-packages pytesseract opencv-python rpi_ws281x adafruit-circuitpython-neopixel

# Install ttspico
sudo apt-get install libttspico-utils

# Verify Camera is configured
X=`libcamera-still -o test.jpg 2>&1|grep Failed`

if [ -z "$X" ];
then
        echo "Found Camera OK"
else
	echo $X
        echo "NO Camera Detected! SEE DOCS Troubleshooting section."
fi 

# Configure asound for desktopless environment
echo "defaults.pcm.card 2
defaults.ctl.card 2
" | sudo /etc/asound.conf

sudo chown root:root /etc/asound.conf

# Power On/Off control button, enable GPIO port
cp /boot/config.txt /boot/config.txt.bak
# echo " "  >> /boot/config.txt
# echo "# Enable power On/Off swith control ============="  >> /boot/config.txt
# echo "dtoverlay=gpio-shutdown" >> /boot/config.txt

# echo " "  >> /boot/config.txt
# echo "# Enable Camera" >> /boot/config.txt
# echo "start_x=1"       >> /boot/config.txt
# echo "gpu_mem=128"     >> /boot/config.txt


# Install custom software
crontab ./cronfile
echo "Crontab entry installed for pi userid. OK"
 
# FINISHED!
echo "Finished installation. See Readme.md for more info"
echo "Reboot your pi now:  $ sudo reboot"
echo 

