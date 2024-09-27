#!/bin/bash

#/var/www/html/openWB/runs/mart95.sh
#/var/www/html/openWB/runs/mart96.sh
#/var/www/html/openWB/runs/mart97.sh

resp=$(curl -s http://192.168.208.72/rpc/Shelly.GetStatus )
if true  ; then
 echo "resp:"
 echo $resp
 echo $resp | tr "," "\n" | tr '"' ' '  | tr ":" "="
fi

function cutter()   # suchtext varname
{
 declare -n n=$2
 x=$(echo $resp | tr "," "\n" | tr '"' ' ' | grep "$1" | tr ":" "=")
 value="${x#*=}"
 if [[ "${value:0:1}" == "'" ]] ; then
    value="${value:1:-1}"
 fi
 n=$value
}

if [ ! -f /home/pi/em3peg.csv ] ; then
 echo "time;w1;w2;w3;wsum;wh1;wh2;wh3;whsum" >/home/pi/em3peg.csv
fi

ts=$(date +"%Y-%m-%d %H:%M:%S")
cutter "a_act_power" W1
cutter "b_act_power" W2
cutter "c_act_power" W3
wsum=$(echo "$W1 + $W2 + $W3 " | bc )
W1=$(echo $W1 | tr "." "," )
W2=$(echo $W2 | tr "." "," )
W3=$(echo $W3 | tr "." "," )
wsum=$(echo $wsum | tr "." "," )
# echo "Watt $W1 $W2 $W3 wsum $wsum Watt"

cutter "a_total_act_e" kw1
cutter "b_total_act_e" kw2
cutter "c_total_act_e" kw3
kwsum=$(echo "$kw1 + $kw2 + $kw3 " | bc )
kw1=$(echo $kw1 | tr "." "," )
kw2=$(echo $kw2 | tr "." "," )
kw3=$(echo $kw3 | tr "." "," )
kwsum=$(echo $kwsum | tr "." "," )
# echo "KW  $kw1 $kw2 $kw3 kwsum $kwsum wh"
line="\"$ts\";$W1;$W2;$W3;$wsum;$kw1;$kw2;$kw3;$kwsum"
echo $line >>/home/pi/em3peg.csv

exit 0
