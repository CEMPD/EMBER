#!/bin/tcsh -f

set log = /work/users/t/r/tranhuy/ember_2024/smoke/intermed/ptfire-rx-us/logs/smkinven_ptfire-rx-us_apr_ember_2024.log

grep -a ERROR -A 1 $log | grep Region|sort -u
grep -a ERROR -A 5 $log | awk '/ERROR:/ {capture=1} /^[ \t]*Region:/ && capture {region=substr($2, 7); plant=$4; char1=$6; char2=$8} /^[ \t]*Char3:/ && capture {char3=$2; char4=substr($4, 11); print region "," char4 "," plant "," char1 "," char2 "," char3; capture=0}' | sort -u
#grep -a ERROR -A 5 $log | awk '/ERROR:/ {capture=1} /^[ \t]*Region:/ && capture {region=substr($2, 7); plant=$4; char1=$6; char2=$8} /^[ \t]*Char3:/ && capture {char3=$2; char4=substr($4, 11); print region "," char4 "," plant "," char1 "," char2 "," char3; capture=0}' | sort -u

#grep -a ERROR -A 5 /proj/ie/proj/GSA-EMBER/BlueSky/ember_2023/smoke/intermed/ptfire-rx/logs/smkinven_ptfire-rx_apr_ember2023.log \
#| awk '/Region:/ {r=$0} /Char3:/ {print r " " $0}' | sort -u

#grep -a ERROR -A 5 $log | awk '/^ERROR:/ {capture=1; region=""; char3=""}  /^WARNING:/ {capture=0}  /Region:/ && capture {region=$0}  /Char3:/ && capture {char3=$0; print region " " char3; capture=0}' | sort -u
#grep -a ERROR -A 5 $log | awk '  /^ERROR:/ {capture=1; region=""; char3=""}  /^WARNING:/ {capture=0}  /^[[:space:]]*Region:/ && capture {region=$0}  /^[[:space:]]*Char3:/ && capture {char3=$0; print region " " char3; capture=0}' | sort -u
