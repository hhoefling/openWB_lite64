#!/bin/bash
OPENWBBASEDIR=$(cd `dirname $0`/../../ && pwd)
RAMDISKDIR="$OPENWBBASEDIR/ramdisk"
MODULEDIR=$(cd `dirname $0` && pwd)
CONFIGFILE="$OPENWBBASEDIR/openwb.conf"
LOGFILE="$RAMDISKDIR/soc.log"
DMOD="EVSOC"
CHARGEPOINT=$1


# check if config file is already in env
if [[ -z "$debug" ]]; then
	echo "soc_citogo: Seems like openwb.conf is not loaded. Reading file."
	# try to load config
	. $OPENWBBASEDIR/loadconfig.sh
	# load helperFunctions
	. $OPENWBBASEDIR/helperFunctions.sh
fi

# debug=1


case $CHARGEPOINT in
	2)
		# second charge point
		ladeleistung=$(<$RAMDISKDIR/llaktuells1)
		soctimerfile="$RAMDISKDIR/soctimer1"
		socfile="$RAMDISKDIR/soc1"
		intervall=$((60 * 6))
		intervallladen=$((10 * 6))
		username=$soc2user
		password=$soc2pass
		opts=$soc2opts
		;;
	*)
		# defaults to first charge point for backward compatibility
		# set CHARGEPOINT in case it is empty (needed for logging)
		CHARGEPOINT=1
		ladeleistung=$(<$RAMDISKDIR/llaktuell)
		soctimerfile="$RAMDISKDIR/soctimer"
		socfile="$RAMDISKDIR/soc"
		intervall=$((60 * 6))
		intervallladen=$((10 * 6))
		username=$socuser
		password=$socpass
		opts=$socopts
		;;
esac

incrementTimer()
{
	case $dspeed in
		1)
			# Regelgeschwindigkeit 10 Sekunden
			ticksize=1
			;;
		2)
			# Regelgeschwindigkeit 20 Sekunden
			ticksize=2
			;;
		3)
			# Regelgeschwindigkeit 60 Sekunden
			ticksize=1
			;;
		*)
			# Regelgeschwindigkeit unbekannt
			ticksize=1
			;;
	esac
	soctimer=$((soctimer+$ticksize))
	echo $soctimer > $soctimerfile
}



getAndWriteSoc()
{
	openwbDebugLog ${DMOD} 0 "Lp$CHARGEPOINT: Requesting SoC [debug:$debug] $opts "
	echo 0 > $soctimerfile  

    start=`date +%s`
	python3 $MODULEDIR/callskoda.py -u $username -p $password -l $CHARGEPOINT -d $debug $opts >>$LOGFILE 2>&1
    end=`date +%s`
	runtime=$((end-start))

# Falls carinfo erzeugt wurde diese an pi verschenken
    if [ -f /var/www/html/openWB/ramdisk/carinfo_* ] ; then
      sudo chown pi:pi /var/www/html/openWB/ramdisk/carinfo_*
    fi
    
}

if [ "$username" == "" ] ; then
  openwbDebugLog ${DMOD} 0 "Lp$CHARGEPOINT: No User, no aktion"
  exit 1
fi
if [ "$password" == "" ] ; then
  openwbDebugLog ${DMOD} 0 "Lp$CHARGEPOINT: No Passowrd, no aktion"
  exit 2
fi


soctimer=$(<$soctimerfile)
#openwbDebugLog ${DMOD} 0 " Lp$CHARGEPOINT: timer = $soctimer"
if (( ladeleistung > 500 )); then
	if (( soctimer < intervallladen )); then
		incrementTimer
		# openwbDebugLog ${DMOD} 0 "Lp$CHARGEPOINT: Charging, but nothing to do yet. Incrementing timer to $soctimer from $intervallladen"
	else
		getAndWriteSoc
	fi
else
	if (( soctimer < intervall )); then
		incrementTimer
		# openwbDebugLog ${DMOD} 0 "Lp$CHARGEPOINT: Nothing to do yet. Incrementing timer to $soctimer from $intervall."
	else
		getAndWriteSoc
	fi
fi

          