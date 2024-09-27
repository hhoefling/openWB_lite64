#!/bin/bash
OPENWBBASEDIR=$(cd `dirname $0`/../../ && pwd)
MODULEDIR=$(cd `dirname $0` && pwd)

# check if config file is already in env
if [[ -z "$debug" ]]; then
	. $OPENWBBASEDIR/loadconfig.sh
fi


timeout -k 9 3 python3 $MODULEDIR/rct_read_evu_info.py --ip=$bezug1_ip 2>&1
rc=$?
if  [[ ($rc == 143)  || ($rc == 124) ]] ; then
  echo "EVU-Info Script timed out"
fi
exit $rc
