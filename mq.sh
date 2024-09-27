#!/bin/bash



mosquitto_sub  -v -t openWB/# -T openWB/graph/# | while read a b ; do
  a=${a/openWB\//}
  echo -e "$a  \t= [$b]"
done

