#!/bin/bash

resp=$(curl -s http://192.168.208.74/rpc/Shelly.GetStatus )
if false  ; then
 echo "resp:"
 echo $resp
 echo $resp | tr "," "\n" | tr '"' ' '  | tr ":" "="
fi


function cutter()   # suchtext varname
{
 declare -n n=$2
 x=$(echo $resp | tr "," "\n" | tr '"' ' ' | grep "$1" | tr ":" "=" | head -n 1)
 value="${x#*=}"
 if [[ "${value:0:1}" == "'" ]] ; then
    value="${value:1:-1}"
 fi
# echo "$x"
 n=$value
}

if [ ! -f /home/pi/em3p33.csv ] ; then
 echo "time;w1;wh3" >/home/pi/em3p33.csv
fi

ts=$(date +"%Y-%m-%d %H:%M:%S")
cutter "act_power" W1
wsum=$(echo "$W1" | bc )
W1=$(echo $W1 | tr "." "," )
wsum=$(echo $wsum | tr "." "," )
# echo "Watt $W1 wsum $wsum Watt"

cutter "total_act_e" kw1
kwsum=$(echo "$kw1 " | bc )
kw1=$(echo $kw1 | tr "." "," )
kwsum=$(echo $kwsum | tr "." "," )
# echo "KW  $kw1 kwsum $kwsum wh"
line="\"$ts\";$W1;$kw1"
echo $line >>/home/pi/em3p33.csv

exit 0
