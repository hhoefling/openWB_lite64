#!/bin/bash

SELF=$(cd `dirname $0`   &&  pwd)
OPENWBBASEDIR=$(cd `dirname $0`/../../ && pwd)
# check if config file is already in env
cd $OPENWBBASEDIR 
if [[ -z "$debug" ]]; then
	source ./loadconfig.sh
	source ./helperFunctions.sh
fi


if [ -n "$bezug1_ip" ]; then
	  opt=""
 else
	    echo "$0 Debughilfe bezug1_ip parameter not supplied use 192.168.208.63"
	    bezug1_ip=192.168.208.63
	    # opt=" -v"
		opt=""     # Kein echo!
fi


python3 /var/www/html/openWB/modules/bezug_rct2/rct_read_bezug.py $opt --ip=$bezug1_ip >/dev/null

read wattbezug </var/www/html/openWB/ramdisk/wattbezug
echo $wattbezug
exit 0
