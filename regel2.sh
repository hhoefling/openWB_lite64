#!/bin/bash
cd /var/www/html/openWB/ || exit 1
source helperFunctions.sh
source loadconfig.sh
s=$(set | wc -l)
rlog RGL $s lines
sleep 6
openwbDebugLog "MAIN" 0 "**** regel2.sh ends #####################"


