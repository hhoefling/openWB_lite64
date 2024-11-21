#!/bin/bash
cd /var/www/html/openWB
. /var/www/html/openWB/loadconfig.sh

# set mode to stop and flags in ramdisk and broker to indicate current update state
mosquitto_pub -t openWB/set/ChargeMode -r -m "3"
mosquitto_pub -t openWB/system/updateInProgress -r -m "1"
echo 1 > /var/www/html/openWB/ramdisk/updateinprogress
echo 1 > /var/www/html/openWB/ramdisk/bootinprogress
msg="Update im Gange, bitte warten bis die Meldung nicht mehr sichtbar ist" 
echo $msg > /var/www/html/openWB/ramdisk/lastregelungaktiv
mosquitto_pub -t "openWB/global/strLastmanagementActive" -r -m "$msg"
echo $msg > /var/www/html/openWB/ramdisk/mqttv/lastregelungaktiv
chmod 777 var/www/html/openWB/ramdisk/mqttv/lastregelungaktiv

if [[ "$releasetrain" == "stable" ]]; then
	train=stable17
else
	train=$releasetrain
fi

# check for ext openWB on configured chargepoints and start update
if [[ "$evsecon" == "extopenwb" ]]; then
	echo "starting update on extOpenWB on LP1"
	mosquitto_pub -t openWB/set/system/releaseTrain -r -h $chargep1ip -m "$releasetrain"
	mosquitto_pub -t openWB/set/system/PerformUpdate -r -h $chargep1ip -m "1"
fi
if [[ $lastmanagement == "1" ]]; then
	if [[ "$evsecons1" == "extopenwb" ]]; then
		echo "starting update on extOpenWB on LP2"
		mosquitto_pub -t openWB/set/system/releaseTrain -r -h $chargep2ip -m "$releasetrain"
		mosquitto_pub -t openWB/set/system/PerformUpdate -r -h $chargep2ip -m "1"
	fi
fi
if [[ $lastmanagements2 == "1" ]]; then
	if [[ "$evsecons2" == "extopenwb" ]]; then
		echo "starting update on extOpenWB on LP3"
		mosquitto_pub -t openWB/set/system/releaseTrain -r -h $chargep3ip -m "$releasetrain"
		mosquitto_pub -t openWB/set/system/PerformUpdate -r -h $chargep3ip -m "1"
	fi
fi
for i in $(seq 4 8); do
	lastmanagementVar="lastmanagementlp$i"
	evseconVar="evseconlp$i"
	if [[ ${!lastmanagementVar} == "1" ]]; then
		if [[ ${!evseconVar} == "extopenwb" ]]; then
			echo "starting update on extOpenWB on LP$i"
			chargepIpVar="chargep${i}ip"
			mosquitto_pub -t openWB/set/system/releaseTrain -r -h ${!chargepIpVar} -m "$releasetrain"
			mosquitto_pub -t openWB/set/system/PerformUpdate -r -h ${!chargepIpVar} -m "1"
		fi
	fi
done

sleep 15


# fetch new release from GitHub

cp -p /var/www/html/openWB/openwb.conf /tmp/openwb.conf
sudo -u pi git fetch origin
sudo -u pi git reset --hard origin/$train
sudo cp -p /tmp/openwb.conf /var/www/html/openWB/openwb.conf

# set permissions
cd /var/www/html/
sudo chown -R pi:pi openWB 
sudo chown -R www-data:www-data openWB/web/backup
sudo chown -R www-data:www-data openWB/web/tools/upload
sudo chmod 777 openWB/web/backup
sudo chmod 777 openWB/web/tools/upload
sudo chmod 777 openWB/web/lade.log
sudo chmod 777 openWB/openwb.conf
sudo chmod -R +x openWB/modules/*
sudo chmod -R +x openWB/runs/*
sudo chmod +x openWB/*.sh
sudo chmod 777 openWB/ramdisk/*


sleep 2

# now treat system as in booting state
nohup sudo -u pi /var/www/html/openWB/runs/atreboot.sh >> /var/log/openWB.log 2>&1 &

