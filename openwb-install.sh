#!/bin/bash

## now with lf

if (( $(id -u) != 0 )); then
        echo "this script has to be run as user root or with sudo"
        exit 1
fi
if uname -a | grep -q x86_64 ; then isPC=1; else isPC=0; fi;
if uname -a | grep -q 5.15 ; then isBullseye=1; else isBullseye=0; fi;
read debvers </etc/debian_version
debver=${debvers%.*}

OPENWBBASEDIR=/var/www/html/openWB
export openwbgiturl="https://github.com/hhoefling/openWB_lite64.git"
# export openwbgiturl="http://www.hhoefling.local:3000/gitea/openwb67.git"
echo "installing openWB from $openwbgiturl into \"${OPENWBBASEDIR}\" on Debian $debver"
echo "isPC:$isPC"
echo "Debian:$debver ($debvers)"

if (( isPC == 0 )) ; then
  if which tvservice >/dev/null 2>&1  && sudo tvservice -s | grep -qF "[LCD], 800x480 @ 60.00Hz" ; then
    echo "LCD detected"
    hasLCD=1
  else
    echo "no LCD detected"
    hasLCD=0
  fi
fi
if (( debver <= 9 )) ; then
  echo "Instzalling on Stretch"
elif (( debver == 10 )) ; then
  echo "Instzalling on Buster"
elif (( debver == 11 )) ; then
  echo "Instzalling on Bullseye"
else
  echo "Unbekannte Debian version. Installation abgebrochen"
fi


echo "install required packages..."
if (( debver <= 9 )) ; then
    # check for outdated sources.list (Stretch only)
    if grep -q -e "^deb http://raspbian.raspberrypi.org/raspbian/ stretch" /etc/apt/sources.list; then
	   echo "sources.list outdated! upgrading..."
	   sudo sed -i "s/^deb http:\/\/raspbian.raspberrypi.org\/raspbian\/ stretch/deb http:\/\/legacy.raspbian.org\/raspbian\/ stretch/g" /etc/apt/sources.list
    else
	   echo "sources.list already updated"
    fi
fi

apt-get update
dpkg -l >/home/pi/firstdpkg.txt
if (( isPC == 0 )) ; then
    apt-get -q -y install raspberrypi-kernel-headers 
else
    apt-get -q -y install linux-kernel-headers 
fi
apt-get -q -y install jq i2c-tools task-spooler git vim at bc
apt-get -q -y install mosquitto mosquitto-clients socat sshpass
# bullseye hat kein python-pip mehr, daher einzeln da sonst abbruch
apt-get -q -y install python-pip
apt-get -q -y install python3-pip
if (( debver < 11 )) ; then
    # Buster/Stretch
	apt-get -q -y install python-pip python-rpi.gpioa
else
	# bullseye
	apt-get -q -y install python3-pip python3-rpi.gpio
fi

echo "Install appache2"
apt-get -q -y install apache2 php php-gd php-curl php-xml php-json libapache2-mod-php
systemctl restart apache2
echo "done"

if (( isPC == 0 )) ; then
  if (( hasLCD > 0 )) ; then
    echo "install chrome browser..."
    apt-get -q -y install chromium-browser
  else
    echo "no LCD, no chrome"
    apt-get -q -y install multitail
  fi
fi


needreboot=0
if (( isPC == 0 )) ; then
  if ! grep -Fq "ipv6.disable=1" /boot/cmdline.txt
  then
   echo "Disable ipv6, need reboot"
   line="$(</boot/cmdline.txt)"
   echo "$line ipv6.disable=1" >/boot/cmdline.txt
   needreboot=1
  else
   echo "ipv6 allready disabled via cmdline.txt"
  fi

  if ! grep -Fq "dtoverlay=vc4-fkms-v3d"  /boot/config.txt
  then
    echo "switch to dtoverlay=vc4-fkms-v3d"
    sed -i "s/^dtoverlay=vc4-kms-v3d/dtoverlay=vc4-fkms-v3d/" /boot/config.txt
    needreboot=1
  else
    echo "allready use dtoverlay=vc4-fkms-v3d"
  fi
  if [ -r /etc/chromium.d/01-nooptim ] 
  then
    echo "chromioptim...ok"
  else
    echo 'export CHROMIUM_FLAGS="$CHROMIUM_FLAGS --disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints" ' >/etc/chromium.d/01-nooptim
    echo "file /etc/chromium.d/01-nooptim created"
  fi
fi


echo "check for timezone"
if  grep -Fxq "Europe/Berlin" /etc/timezone
then
	echo "...ok"
else
	echo 'Europe/Berlin' > /etc/timezone
	dpkg-reconfigure -f noninteractive tzdata
	cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime
	echo "...changed"
fi

echo "check for i2c bus"
if grep -Fxq "i2c-bcm2835" /etc/modules
then
	echo "...ok"
else
	echo "i2c-dev" >> /etc/modules
	echo "i2c-bcm2708" >> /etc/modules
	echo "snd-bcm2835" >> /etc/modules
	echo "dtparam=i2c1=on" >> /etc/modules
	echo "dtparam=i2c_arm=on" >> /etc/modules
fi

echo "check for tmp"
if [ ! -d /var/www/html/tmp ]; then
	cd /var/www/html/
	mkdir tmp
	chown www-data:www-data tmp
	chmod 0777 tmp
	echo "/var/www/html/tmp created"
else
	echo "...ok"
fi
echo "check for initial git clone"
if [ ! -d /var/www/html/openWB/web ]; then
	cd /var/www/html/
	mkdir openWB
 	chown pi:pi openWB
	chmod 0777 openWB
	sudo -u pi git clone --branch master ${openwbgiturl} openWB
	chown -R pi:pi openWB 
	sudo -u pi git config --global --add safe.directory /var/www/html/openWB
	sudo -u pi git config --global credential.helper store
	cd openWB
	sudo -u pi git fetch origin
	sudo -u pi git reset --hard origin/master  
	echo "... git cloned"
	cd /var/www/html/openWB
	sudo cp -p runs/files/openwb.conf.default openwb.conf
	ls -l openwb.*
	echo "... openwb.conf activated"
else
	echo "...ok"
fi


if ! grep -Fq "bootmodus=" /var/www/html/openWB/openwb.conf
then
	echo "bootmodus=3" >> /var/www/html/openWB/openwb.conf
fi
sudo -u pi /var/www/html/openWB//runs/replaceinconfig.sh "isPC=" "$isPC"
sudo -u pi /var/www/html/openWB//runs/replaceinconfig.sh "hasLCD=" "$hasLCD"

echo "check for ramdisk" 
if grep -Fxq "tmpfs /var/www/html/openWB/ramdisk tmpfs nodev,nosuid,size=32M 0 0" /etc/fstab 
then
	echo "...ok"
else
	mkdir -p /var/www/html/openWB/ramdisk
	echo "tmpfs /var/www/html/openWB/ramdisk tmpfs nodev,nosuid,size=32M 0 0" >> /etc/fstab
	mount -a
	echo "0" > /var/www/html/openWB/ramdisk/ladestatus
	echo "0" > /var/www/html/openWB/ramdisk/llsoll
	echo "0" > /var/www/html/openWB/ramdisk/soc
	chown pi:pi /var/www/html/openWB/ramdisk/*
	chmod 0777 /var/www/html/openWB/ramdisk/*
	echo "...created"
fi

echo "check for crontab root"
if grep -Fq "@reboot sleep 10 && /home/pi/wlan.sh" /var/spool/cron/crontabs/root
then
	echo "...ok"
else
	echo "@reboot sleep 10 && /home/pi/wlan.sh" > /tmp/tocrontab
	crontab -l -u root | cat - /tmp/tocrontab | crontab -u root -
	rm /tmp/tocrontab
	echo "...added"
	crontab -l -u root
fi
echo "check for crontab pi"
if grep -Fq "/var/www/html/openWB/runs/regler.sh" /var/spool/cron/crontabs/pi
then
	echo "...ok"
else
	(
	echo "# openWB Crontab for user pi"
	echo "@reboot /var/www/html/openWB/runs/atreboot.sh >> /var/log/openWB.log 2>&1 "
	echo "1 0 * * * /var/www/html/openWB/runs/cronnightly.sh >> /var/log/openWB.log 2>&1 " 
	echo "*/5 * * * * /var/www/html/openWB/runs/cron5min.sh >> /var/log/openWB.log 2>&1 "
	echo "* * * * * /var/www/html/openWB/regler.sh >> /var/log/openWB.log 2>&1 "
	) >/tmp/tocrontab
# ersetzen statt anhaengen
    #### crontab -l -u pi | cat - /tmp/tocrontab | crontab -u pi -
	cat /tmp/tocrontab | crontab -u pi -
	rm /tmp/tocrontab
	echo "...replaced"
	crontab -l -u pi
fi

# start mosquitto
sudo service mosquitto start

# check for mosquitto configuration
if [ ! -f /etc/mosquitto/conf.d/openwb.conf ]; then
	echo "updating mosquitto config file"
	sudo cp /var/www/html/openWB/runs/files/mosquitto.conf /etc/mosquitto/conf.d/openwb.conf
	if (( debver <= 9 )) ; then
		sudo sed -i "s/^socket_domain ipv4/# socket_domain ipv4/g" /etc/mosquitto/conf.d/openwb.conf
		echo "modifiy mosquitto openwb.conf for Stretch"
	fi
	sudo cp "/etc/ssl/certs/ssl-cert-snakeoil.pem" "/etc/mosquitto/certs/openwb.pem"
	sudo cp "/etc/ssl/private/ssl-cert-snakeoil.key" "/etc/mosquitto/certs/openwb.key"
	sudo chgrp mosquitto "/etc/mosquitto/certs/openwb.key"
#	sudo service mosquitto reload
	sudo service mosquitto restart
fi

echo "disable cronjob logging"
if grep -Fxq "EXTRA_OPTS=\"-L 0\"" /etc/default/cron
then
	echo "...ok"
else
	echo "EXTRA_OPTS=\"-L 0\"" >> /etc/default/cron
fi


# set upload limit in php
echo "fix upload limit..."
for d in /etc/php/*/apache2/conf.d ; do
	fn="$d/21-uploadlimit.ini"
	fnold="$d/20-uploadlimit.ini"
	[ -f "$fnold" ] && rm "$fnold"
	if [ ! -f "$fn" ]; then
		echo -e 'upload_max_filesize = 300M\npost_max_size = 300M' >$fn
		echo "Fix upload limit in $d and switch to v. 21"
        echo "$fn fixed"
		#restartService=1
	fi
done

echo "installing pymodbus"
if (( isBullseye == 0 )) ; then
    # Buster/Stretch
    sudo pip install  -U pymodbus
    sudo pip3 install -U --force-reinstall pymodbus==2.4.0
else
    # bullseye
    sudo pip3 install -U --force-reinstall pymodbus==2.5.3
fi
sudo pip3 install --upgrade requests

echo "check for paho-mqtt"
if python3 -c "import paho.mqtt.publish as publish" &> /dev/null; then
	echo 'mqtt installed...'
else
	# sudo pip3 install paho-mqtt
	# use latest 1.x (1.6.1)
	sudo pip3 install "paho-mqtt<2.0.0"
fi

if (( isBullseye == 0 )) ; then
    # Buster/Stretch
	#Adafruit install
	echo "check for MCP4725"
	if python -c "import Adafruit_MCP4725" &> /dev/null; then
		echo 'Adafruit_MCP4725 installed...'
	else
		sudo pip install Adafruit_MCP4725
	fi
fi

echo "pi ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/010_pi-nopasswd
echo "www-data ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/010_pi-nopasswd

chmod 777 /var/www/html/openWB/openwb.conf
chmod +x /var/www/html/openWB/modules/*
chmod +x /var/www/html/openWB/runs/*
chmod +x /var/www/html/openWB/*.sh
touch /var/log/openWB.log
chmod 777 /var/log/openWB.log
touch /var/log/openwb.error.log
chmod 777 /var/log/openwb.error.log


# check links for standart theme
(
 cd /var/www/html/openWB/web/themes/standard
 [ ! -r theme.html ]           && ln -s  ../dark/theme.html .
)

dpkg -l >/home/pi/lastdpkg.txt
diff  /home/pi/firstdpkg.txt /home/pi/lastdpkg.txt >/home/pi/diffdpkg.txt
rm /home/pi/firstdpkg.txt /home/pi/lastdpkg.txt



if ! grep -Fq "openwbgiturl=" /var/www/html/openWB/openwb.conf
then
	echo "openwbgiturl=$openwbgiturl" >> /var/www/html/openWB/openwb.conf
else
  /var/www/html/openWB/runs/replaceinconfig.sh "openwbgiturl=" "$openwbgiturl"
fi

if (( needreboot == 1 )); then
  echo "***************************"
  echo "please reboot and restart installation"A
  echo "***************************"
  echo "do reboot"
  exit 0
fi
 
echo
echo Now calling atreboot.sh as user pi ... 
echo
sudo -u pi /var/www/html/openWB/runs/atreboot.sh


