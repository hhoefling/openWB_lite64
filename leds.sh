#!/bin/bash
openwbDebugLog "MAIN" 1 "source leds.sh"

ledsteuerung() {
    openwbDebugLog "MAIN" 1 "ledsteuerung called"


	read ledstatus <ramdisk/ledstatus
	read lademodus <ramdisk/lademodus
	read ladestatus <ramdisk/ladestatus
	#0 sofort
	#1 min pv
	#2 nur pv
	#3 stop
	#4 standby
	ledrunning=$(ps aux |grep '[l]eds.py' | awk '{print $2}')

    if (( ladestatus == 1 ));then          # 1= Strom wird angeboten
		if (( lademodus == $SOFORT0 )); then
			if [[ $ledstatus != $ledsofort ]]; then
				if [ ! -z "$ledrunning" ]; then
					sudo kill $(ps aux |grep '[l]eds.py' | awk '{print $2}')
				fi
				sudo python runs/leds.py $ledsofort &
				echo $ledsofort > ramdisk/ledstatus
			fi
		fi
		if (( lademodus == $MINPV1 )); then
			if [[ $ledstatus != $ledminpv ]]; then
				if [ ! -z "$ledrunning" ]; then
					sudo kill $(ps aux |grep '[l]eds.py' | awk '{print $2}')
				fi
				sudo python runs/leds.py $ledminpv &
				echo $ledminpv > ramdisk/ledstatus
			fi
		fi
		if (( lademodus == $NURPV2 )); then
			if [[ $ledstatus != $lednurpv ]]; then
				if [ ! -z "$ledrunning" ]; then
					echo "kill"
					sudo kill $(ps aux |grep '[l]eds.py' | awk '{print $2}')
				fi
				sudo python runs/leds.py $lednurpv &
				echo $lednurpv > ramdisk/ledstatus
			fi
		fi
		if (( lademodus == $STOP3 )); then
			if [[ $ledstatus != $ledstop ]]; then
				if [ ! -z "$ledrunning" ]; then
					sudo kill $(ps aux |grep '[l]eds.py' | awk '{print $2}')
				fi
				sudo python runs/leds.py $ledstop &
				echo $ledstop > ramdisk/ledstatus
			fi
		fi
		if (( lademodus == $STANDBY4 )); then
			if [[ $ledstatus != $ledstandby ]]; then
				if [ ! -z "$ledrunning" ]; then
					sudo kill $(ps aux |grep '[l]eds.py' | awk '{print $2}')
				fi
				sudo python runs/leds.py $ledstandby &
				echo $ledstandby > ramdisk/ledstatus
			fi
		fi
	else
		if (( lademodus == $SOFORT0 )); then
			if [[ $ledstatus != $led0sofort ]]; then
				if [ ! -z "$ledrunning" ]; then
					sudo kill $(ps aux |grep '[l]eds.py' | awk '{print $2}')
				fi
				sudo python runs/leds.py $led0sofort &
				echo $led0sofort > ramdisk/ledstatus
			fi
		fi
		if (( lademodus == $MINPV1 )); then
			if [[ $ledstatus != $led0minpv ]]; then
				if [ ! -z "$ledrunning" ]; then
					sudo kill $(ps aux |grep '[l]eds.py' | awk '{print $2}')
				fi
				sudo python runs/leds.py $led0minpv &
				echo $led0minpv > ramdisk/ledstatus
			fi
		fi
		if (( lademodus == $NURPV2 )); then
			if [[ $ledstatus != $led0nurpv ]]; then
				if [ ! -z "$ledrunning" ]; then
					echo "kill"
					sudo kill $(ps aux |grep '[l]eds.py' | awk '{print $2}')
				fi
				sudo python runs/leds.py $led0nurpv &
				echo $led0nurpv > ramdisk/ledstatus
			fi
		fi
		if (( lademodus == $STOP3 )); then
			if [[ $ledstatus != $led0stop ]]; then
				if [ ! -z "$ledrunning" ]; then
					sudo kill $(ps aux |grep '[l]eds.py' | awk '{print $2}')
				fi
				sudo python runs/leds.py $led0stop &
				echo $led0stop > ramdisk/ledstatus
			fi
		fi
		if (( lademodus == $STANDBY4 )); then
			if [[ $ledstatus != $led0standby ]]; then
				if [ ! -z "$ledrunning" ]; then
					sudo kill $(ps aux |grep '[l]eds.py' | awk '{print $2}')
				fi
				sudo python runs/leds.py $led0standby &
				echo $led0standby > ramdisk/ledstatus
			fi
		fi
	fi

}
