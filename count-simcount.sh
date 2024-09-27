#!/bin/bash



############### profiling Anf
ptx=0
pt=0
ptstart()
{
  # ptx=$(( ${EPOCHREALTIME/[\,\.]/} / 1000 )) # debian-11
  ptx=$(date +"%s%N")           # debian-10
  ptx=$(( ptx / 1000 / 1000))   # debian-10
}
export -f ptstart

ptend()
{
 local txt=${1:-}
 local max=${2:-200}
 local te
  # te=$(( ${EPOCHREALTIME/[\,\.]/} / 1000 )) debian-11
 te=$(date +"%s%N")             # debian-11
 te=$(( te / 1000 / 1000 ))     # debian-11

 pt=$(( te - ptx))
 if (( pt > max ))  ; then
   #openwbDebugLog "DEB" 1 "TIME **** ${txt} needs $pt ms. (max:$max)"
   #openwbDebugLog "MAIN" 2 "TIME **** ${txt} needs $pt ms. (max:$max)"
   echo "TIME **** ${txt} needs $pt ms. (max:$max)"
 fi
}
export -f ptend


ptstart

echo "0" >ramdisk/xx1watt0pos
echo "0" >ramdisk/xx1watt0neg

for i in {1..100}
do
  pypy /var/www/html/openWB/runs/simcount.py 110 xx1 xx1_wh xx1_whe
done
ptend "time" 0


pypy -V


exit 0


pi3b+ streatch
root@openWB:/var/www/html/openWB# ./count-simcount.sh q
TIME **** time needs 6069 ms. (max:0)
Python 2.7.13
root@openWB:/var/www/html/openWB# ./count-simcount.sh q
TIME **** time needs 6507 ms. (max:0)
Python 2.7.13
root@openWB:/var/www/html/openWB# ./count-simcount.sh q
TIME **** time needs 5913 ms. (max:0)
Python 2.7.13



pi3b+ streatch
root@openWB:/var/www/html/openWB# ./count-simcount.sh q
TIME **** time needs 14722 ms. (max:0)
Python 3.5.3
root@openWB:/var/www/html/openWB# ./count-simcount.sh q
TIME **** time needs 14791 ms. (max:0)
Python 3.5.3
root@openWB:/var/www/html/openWB# ./count-simcount.sh q
TIME **** time needs 14937 ms. (max:0)
Python 3.5.3
root@openWB:/var/www/html/openWB# ./count-simcount.sh q
TIME **** time needs 14334 ms. (max:0)
Python 3.5.3


pi3b+ buster
root@pi67:/var/www/html/openWB# ./count-simcount.sh
TIME **** time needs 9255 ms. (max:0)
Python 3.7.3
root@pi67:/var/www/html/openWB# ./count-simcount.sh
TIME **** time needs 9284 ms. (max:0)
Python 3.7.3
root@pi67:/var/www/html/openWB# ./count-simcount.sh
TIME **** time needs 9206 ms. (max:0)
Python 3.7.3


pi42GB Bullseye



root@pi61:/var/www/html/openWB# ./count-simcount.sh                            
TIME **** time needs 8923 ms. (max:0)
Python 3.9.2
root@pi61:/var/www/html/openWB# ./count-simcount.sh
TIME **** time needs 8799 ms. (max:0)
Python 3.9.2
root@pi61:/var/www/html/openWB# ./count-simcount.sh
TIME **** time needs 8948 ms. (max:0)
Python 3.9.2




i




