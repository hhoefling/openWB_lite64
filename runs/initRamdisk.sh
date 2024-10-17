#!/bin/bash
# Ramdisk mit initialen Werten befüllen nach Neustart, UP atreboot.sh
# source from atreboot.sh

ri='^-?[0-9]+$'
rf='^-?[0-9\.]+$'


##########################################################
initrdmqtt_i()  # ramname,  topic default 
{
	if [[ -e ramdisk/$1 ]] ; then
		# openwbDebugLog "MAIN" 0 "initrdmqtt ramdisk/$1 allready exists"
		:
	else
		if [[ ! -z $2 ]]; then # oder -n 
			val=$(mosquitto_sub -W 1 -C 1 -t openWB/$2)
			# openwbDebugLog "MAIN" 0 "initrdmqtt read openWB/$1 from mosquito: [$val]"
			if ! [[ $val =~ $ri ]] ; then
				val=$3
				openwbDebugLog "MAIN" 0 "initrdmqtt set $1 and $2 to deFault [$val]"
				mosquitto_pub -t openWB/$2 -r -m "$val"
			else
				openwbDebugLog "MAIN" 0 "initrdmqtt set $1 from $2 to [$val]"
			fi
		else
			val=$3
			openwbDebugLog "MAIN" 0 "initrdmqtt set $1 to deFault [$val]"
		fi
		echo $val > ramdisk/$1
	fi
}


initRamdisk(){
	cd=`pwd`
	openwbDebugLog "MAIN" 2  "INRD Initializing Ramdisk cd:($cd)"
	cd /var/www/html/openWB
	RamdiskPath="ramdisk"

	# Logfiles erstellen
	if [[ ! -L ramdisk/openWB.log ]]; then
		sudo rm -f ramdisk/openWB.log
		ln -s /var/log/openWB.log ramdisk/openWB.log
	fi
	# Errfiles erstellen
	if [[ ! -L ramdisk/openwb.error.log ]]; then
		sudo rm -f ramdisk/openwb.error.log
		ln -s /var/log/openwb.error.log ramdisk/openwb.error.log
	fi
	echo "**** REBOOT ****" >> ramdisk/mqtt.log
	echo "**** REBOOT ****" >> ramdisk/ladestatus.log
	echo "**** REBOOT ****" >> ramdisk/soc.log
	echo "**** REBOOT ****" >> ramdisk/rfid.log
	echo "**** REBOOT ****" >> ramdisk/nurpv.log
	echo "**** REBOOT ****" >> ramdisk/cleanup.log
	echo "**** REBOOT ****" >> ramdisk/smarthome.log
	echo "**** REBOOT ****" >> ramdisk/isss.log
	echo "**** REBOOT ****" >> ramdisk/event.log
	echo "**** REBOOT ****" >> ramdisk/dbg.log
	echo "**** REBOOT ****" >> ramdisk/etprovider.log
	echo "**** REBOOT ****" >> ramdisk/openwb.error.log
	echo "**** REBOOT ****" >> ramdisk/mqtt2mhi.log

	if [ ! -d ramdisk/sm ] ; then
   		mkdir ramdisk/sm
   		sudo chown pi:pi ramdisk/sm
   		sudo chmod 0777  ramdisk/sm
   		openwbDebugLog "MAIN" 2 "INRD Create ramdisk/sm for smarthome "
    fi



	echo "$bootmodus" > ramdisk/lademodus
	echo "" >ramdisk/LadereglerTxt
	echo "" >ramdisk/BatSupportTxt

	# Ladepunkte
	# Variablen noch nicht einheitlich benannt, daher individuelle Zeilen
	echo 0 > ramdisk/errcounterextopenwb
	echo 0 > ramdisk/pluggedin
	echo "nicht angefragt" > ramdisk/evsedintestlp1
	echo "nicht angefragt" > ramdisk/evsedintestlp2
	echo "nicht angefragt" > ramdisk/evsedintestlp3
    echo 0 > ramdisk/restzeitlp1
    echo 0 > ramdisk/restzeitlp2
    echo 0 > ramdisk/restzeitlp3
	echo 0 > ramdisk/restzeitlp1m         # NC
	echo 0 > ramdisk/restzeitlp2m         # NC
	echo 0 > ramdisk/restzeitlp3m         # NC
	echo 0 > ramdisk/aktgeladen
	echo 0 > ramdisk/aktgeladens1
	echo 0 > ramdisk/aktgeladens2
	echo 0 > ramdisk/chargestat
	echo 0 > ramdisk/chargestats1
	echo 0 > ramdisk/chargestatlp3
	echo 0 > ramdisk/ladestatus
	echo 0 > ramdisk/ladestatuss1
	echo 0 > ramdisk/ladestatuss2
:	echo 0 > ramdisk/ladestart
	echo 0 > ramdisk/ladestarts1
	echo 0 > ramdisk/ladestarts2
	echo 0 > ramdisk/gelrlp1
	echo 0 > ramdisk/gelrlp2
	echo 0 > ramdisk/gelrlp3
	echo 0 > ramdisk/ladungaktivlp1
	echo 0 > ramdisk/ladungaktivlp2
	echo 0 > ramdisk/ladungaktivlp3
	echo 0 > ramdisk/lla1
	echo 0 > ramdisk/llas11
	echo 0 > ramdisk/llas21
	echo 0 > ramdisk/lla2
	echo 0 > ramdisk/llas12
	echo 0 > ramdisk/llas22
	echo 0 > ramdisk/lla3
	echo 0 > ramdisk/llas13
	echo 0 > ramdisk/llas23
	echo 0 > ramdisk/llkwh
	echo 0 > ramdisk/llkwhs1
	echo 0 > ramdisk/llkwhs2
	echo 0 > ramdisk/llsoll
	echo 0 > ramdisk/llsolls1
	echo 0 > ramdisk/llsolls2
	echo 0 > ramdisk/llv1
	echo 0 > ramdisk/llvs11
	echo 0 > ramdisk/llvs21
	echo 0 > ramdisk/llv2
	echo 0 > ramdisk/llvs12
	echo 0 > ramdisk/llvs22
	echo 0 > ramdisk/llv3
	echo 0 > ramdisk/llvs13
	echo 0 > ramdisk/llvs23
	echo 0 > ramdisk/pluggedtimer1
	echo 0 > ramdisk/pluggedladungbishergeladen
	echo 0 > ramdisk/pluggedladungbishergeladenlp2
	echo 0 > ramdisk/pluggedladungbishergeladenlp3
	echo 0 > ramdisk/plugstat
	echo 0 > ramdisk/plugstats1
	echo 0 > ramdisk/plugstatlp3
	echo 0 > ramdisk/llaltnv
	echo 0 > ramdisk/llhz
	echo 0 > ramdisk/llkombiniert
	echo 0 > ramdisk/llkwhges
	echo 0 > ramdisk/llpf1
	echo 0 > ramdisk/llpf2
	echo 0 > ramdisk/llpf3
	echo 0 > ramdisk/llaktuell
	echo 0 > ramdisk/llaktuells1
	echo 0 > ramdisk/llaktuells2
	echo 0 > ramdisk/nachtladen2state
	echo 0 > ramdisk/nachtladen2states1
	echo 0 > ramdisk/nachtladenstate
	echo 0 > ramdisk/nachtladenstates1
#	echo 0 > ramdisk/pluggedtimer1
#	echo 0 > ramdisk/pluggedtimer2
#	echo 0 > ramdisk/pluggedtimerlp3
	echo 0 > ramdisk/progevsedinlp1
	echo 0 > ramdisk/progevsedinlp12000
	echo 0 > ramdisk/progevsedinlp12007
	echo 0 > ramdisk/progevsedinlp2
	echo 0 > ramdisk/progevsedinlp22000
	echo 0 > ramdisk/progevsedinlp22007
	echo 0 > ramdisk/cpulp1counter
	echo 0 > ramdisk/soc
	echo 0 > ramdisk/soc1
	echo 0 > ramdisk/soc1KM
	echo 0 > ramdisk/soc2KM
	echo 0 > ramdisk/soc3KM
	echo 0 > ramdisk/soc1Range
    echo 0 > ramdisk/soc2Range
    echo 0 > ramdisk/socvorhanden
	echo 0 > ramdisk/soc1vorhanden
	echo 0 > ramdisk/tmpsoc
	echo 0 > ramdisk/tmpsoc1
	echo 0 > ramdisk/zielladenkorrektura
	echo 0 > ramdisk/ladungdurchziel
	echo 20000 > ramdisk/soctimer
	echo 20000 > ramdisk/soctimer1
	echo 28 > ramdisk/evsemodbustimer
	touch ramdisk/llog1
	touch ramdisk/llogs1
	touch ramdisk/llogs2

	# rct
	echo 0 > ramdisk/HB_discharge_max
	echo 0 > ramdisk/HB_loadWatt
	echo 0 > ramdisk/HB_load_minutes
	echo 0 > ramdisk/HB_soctarget
	echo 0 > ramdisk/HB_iskalib
	echo 1 > ramdisk/HB_enable_discharge_max
	echo 0 > ramdisk/HB_enable_priceloading

	
	# SmartHome 2.0
	echo 0 > ramdisk/device1_temp0
	echo 0 > ramdisk/device1_temp1
	echo 0 > ramdisk/device1_temp2
	echo 0 > ramdisk/device1_wh
	echo 0 > ramdisk/device2_temp0
	echo 0 > ramdisk/device2_temp1
	echo 0 > ramdisk/device2_temp2
	echo 0 > ramdisk/device2_wh
	echo 0 > ramdisk/device3_wh
	echo 0 > ramdisk/device4_wh
	echo 0 > ramdisk/device5_wh
	echo 0 > ramdisk/device6_wh
	echo 0 > ramdisk/device7_wh
	echo 0 > ramdisk/device8_wh
	echo 0 > ramdisk/device9_wh
	echo 0 > ramdisk/smarthome_device_minhaus_1
	echo 0 > ramdisk/smarthome_device_minhaus_2
	echo 0 > ramdisk/smarthome_device_minhaus_3
	echo 0 > ramdisk/smarthome_device_minhaus_4
	echo 0 > ramdisk/smarthome_device_minhaus_5
	echo 0 > ramdisk/smarthome_device_minhaus_6
	echo 0 > ramdisk/smarthome_device_minhaus_7
	echo 0 > ramdisk/smarthome_device_minhaus_8
	echo 0 > ramdisk/smarthome_device_minhaus_9
	echo 0 > ramdisk/smarthome_device_manual_1
	echo 0 > ramdisk/smarthome_device_manual_2
	echo 0 > ramdisk/smarthome_device_manual_3
	echo 0 > ramdisk/smarthome_device_manual_4
	echo 0 > ramdisk/smarthome_device_manual_5
	echo 0 > ramdisk/smarthome_device_manual_6
	echo 0 > ramdisk/smarthome_device_manual_7
	echo 0 > ramdisk/smarthome_device_manual_8
	echo 0 > ramdisk/smarthome_device_manual_9
# 	echo 0 > ramdisk/smarthomehandlerloglevel

	# evu
	echo 0 > ramdisk/bezuga1
	echo 0 > ramdisk/bezuga2
	echo 0 > ramdisk/bezuga3
	echo 0 > ramdisk/bezugkwh
	echo 0 > ramdisk/bezugw1
	echo 0 > ramdisk/bezugw2
	echo 0 > ramdisk/bezugw3
	echo 0 > ramdisk/einspeisungkwh
	echo 0 > ramdisk/evuhz
	echo 0 > ramdisk/evupf1
	echo 0 > ramdisk/evupf2
	echo 0 > ramdisk/evupf3
	echo 0 > ramdisk/evuv1
	echo 0 > ramdisk/evuv2
	echo 0 > ramdisk/evuv3
	echo 0 > ramdisk/wattbezug

	# pv
	echo 0 > ramdisk/daily_pvkwhk
# NC	echo 0 > ramdisk/daily_pvkwhk1
# NC	echo 0 > ramdisk/daily_pvkwhk2
	echo 0 > ramdisk/monthly_pvkwhk
# NC	echo 0 > ramdisk/monthly_pvkwhk1
# NC	echo 0 > ramdisk/monthly_pvkwhk2
	echo 0 > ramdisk/nurpv70dynstatus
	echo 0 > ramdisk/pv1watt
	echo 0 > ramdisk/pv2a1
	echo 0 > ramdisk/pv2a2
	echo 0 > ramdisk/pv2a3
	echo 0 > ramdisk/pv2kwh
	echo 0 > ramdisk/pv2watt
	echo 0 > ramdisk/pvcounter
	echo 0 > ramdisk/pvecounter
	echo 0 > ramdisk/pvkwh
	echo 0 > ramdisk/pvkwhk
	echo 0 > ramdisk/pvkwhk1
	echo 0 > ramdisk/pvkwhk2
	echo 0 > ramdisk/pv1vorhanden
	echo 0 > ramdisk/pv2vorhanden
	echo 0 > ramdisk/pvwatt
	echo 0 > ramdisk/pvwatt1
	echo 0 > ramdisk/pvwatt2
	echo 0 > ramdisk/yearly_pvkwhk
# NC	echo 0 > ramdisk/yearly_pvkwhk1
# NC	echo 0 > ramdisk/yearly_pvkwhk2

	# bat
	echo 0 > ramdisk/speicher
	echo 0 > ramdisk/speicherekwh
	echo 0 > ramdisk/speicherikwh
	echo 0 > ramdisk/speicherleistung
	echo 0 > ramdisk/speicherleistung1
	echo 0 > ramdisk/speicherleistung2
	echo 0 > ramdisk/speichersoc
	echo 0 > ramdisk/speichersoc2
# HH
	echo 0 > ramdisk/speichervorhanden


	# rfid
	echo "$rfidlist" > ramdisk/rfidlist
	echo 0 > ramdisk/rfidlasttag
	echo 0 > ramdisk/rfidlp1
	echo 0 > ramdisk/rfidlp2
	echo 0 > ramdisk/rfidlp3
	echo 0 > ramdisk/readtag
	echo 0 > ramdisk/tagScanInfoLp1
	echo 0 > ramdisk/tagScanInfoLp2
	echo 0 > ramdisk/tagScanInfoLp3

	# SmartHome 1.0
	echo 0 > ramdisk/hook1akt
	echo 0 > ramdisk/hook1einschaltverzcounter
	echo 0 > ramdisk/hook2akt
	echo 0 > ramdisk/hook2einschaltverzcounter
	echo 0 > ramdisk/hook3akt
	echo 0 > ramdisk/hook3einschaltverzcounter      # fehlte
	echo "$verbraucher1_name" > ramdisk/verbraucher1_name
	echo "$verbraucher2_name" > ramdisk/verbraucher2_name


	echo 0 > ramdisk/verbraucher1_watt
	echo 0 > ramdisk/verbraucher1_wh
	echo 0 > ramdisk/verbraucher1_whe
	echo 0 > ramdisk/verbraucher1vorhanden
	echo 0 > ramdisk/daily_verbraucher1ekwh
	echo 0 > ramdisk/daily_verbraucher1ikwh

	echo 0 > ramdisk/verbraucher2_watt
	echo 0 > ramdisk/verbraucher2_wh
	echo 0 > ramdisk/verbraucher2_whe
	echo 0 > ramdisk/verbraucher2vorhanden
	echo 0 > ramdisk/daily_verbraucher2ekwh
	echo 0 > ramdisk/daily_verbraucher2ikwh
    
	touch ramdisk/ladestophooklp1aktiv # benötigt damit der Ladestopp-WebHook nicht beim Neustart auslöst
	touch ramdisk/abgesteckthooklp1aktiv # benötigt damit der Abgesteckt-WebHook nicht beim Neustart auslöst

	# standard socket
#	echo 0 > ramdisk/socketa
#	echo 0 > ramdisk/socketv
#	echo 0 > ramdisk/socketp
#	echo 0 > ramdisk/socketpf
#	echo 0 > ramdisk/socketkwh
#	echo 0 > ramdisk/socketApproved
#	echo 0 > ramdisk/socketActivated
#	echo 0 > ramdisk/socketActivationRequested

	# diverse Dateien
#	echo 0 > ramdisk/autolocktimer  NC
	echo 0 > ramdisk/blockall
	echo 0 > ramdisk/devicetotal_watt
	echo 0 > ramdisk/etprovidermaxprice
	echo 0 > ramdisk/etproviderprice
	touch ramdisk/etprovidergraphlist
	echo 0 > ramdisk/evseausgelesen
	echo 0 > ramdisk/glattwattbezug
	echo 0 > ramdisk/hausverbrauch
	echo 0 > ramdisk/ipaddress
	echo 0 > ramdisk/ledstatus
	echo 0 > ramdisk/netzschutz
# Yourcharge
#	echo 0 > ramdisk/randomSleepValue
	echo 0 > ramdisk/renewmqtt
	echo 0 > ramdisk/rseaktiv
    echo 0 > ramdisk/rsestatus
	echo 0 > ramdisk/schieflast
	echo 0 > ramdisk/u1p3pstat
	echo 0 > ramdisk/uhcounter
	echo 0 > ramdisk/urcounter
	echo 1 > ramdisk/anzahlphasen
	echo 1 > ramdisk/bootinprogress
	echo 1 > ramdisk/execdisplay
	echo 4 > ramdisk/graphtimer



	initrdmqtt_i pluggedladunglp1startkwh lp/1/plugStartkWh 0
	initrdmqtt_i manual_soc_lp1 lp/1/manualSoc 0
	initrdmqtt_i pluggedladungaktlp1 lp/1/pluggedladungakt 0
	initrdmqtt_i lp1sofortll config/get/sofort/lp/1/current 10

	initrdmqtt_i pluggedladunglp2startkwh lp/2/plugStartkWh 0
	initrdmqtt_i manual_soc_lp2 lp/2/manualSoc 0
	initrdmqtt_i pluggedladungaktlp2 lp/2/pluggedladungakt 0
	initrdmqtt_i lp2sofortll config/get/sofort/lp/2/current 10

	initrdmqtt_i pluggedladunglp3startkwh lp/3/plugStartkWh 0
	initrdmqtt_i manual_soc_lp3 lp/3/manualSoc 0
	initrdmqtt_i pluggedladungaktlp3 lp/3/pluggedladungakt 0
	initrdmqtt_i lp3sofortll config/get/sofort/lp/3/current 10

	initrdmqtt_i lp1phasen "" 0
	initrdmqtt_i lp1enabled "" 1
	initrdmqtt_i restzeitlp1 "" 0
	initrdmqtt_i rfidlp1 "" 0
	initrdmqtt_i boolstopchargeafterdisclp1 "" 0

	initrdmqtt_i lp2phasen "" 0
	initrdmqtt_i lp2enabled "" 1
	initrdmqtt_i restzeitlp2 "" 0
	initrdmqtt_i rfidlp2 "" 0
	initrdmqtt_i boolstopchargeafterdisclp2 "" 0

	initrdmqtt_i lp3phasen "" 0
	initrdmqtt_i lp3enabled "" 1
	initrdmqtt_i restzeitlp3 "" 0
	initrdmqtt_i rfidlp3 "" 0
	initrdmqtt_i boolstopchargeafterdisclp3 "" 0

	initrdmqtt_i sm/maxbatterypower config/get/SmartHome/maxBatteryPower 0
	initrdmqtt_i smartmq config/get/SmartHome/smartmq 1


	sudo chmod 777 ramdisk/*

	openwbDebugLog "MAIN" 2  "INRD Trigger update of logfiles..."
	python3 /var/www/html/openWB/runs/csvcalc.py --input /var/www/html/openWB/web/logging/data/daily/ --output /var/www/html/openWB/web/logging/data/v001/ --partial /var/www/html/openWB/ramdisk/ --mode M >> /var/www/html/openWB/ramdisk/csvcalc.log 2>&1 &
	openwbDebugLog "MAIN" 2  "INRD Ramdisk init done."
}
