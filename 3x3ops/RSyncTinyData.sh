#!/bin/bash
args=("$@")
argssize=${#args[*]}
if [ $argssize -ne 2 ];then
    echo ""
    echo "Usage:   ./RSyncTinyData.sh {detector: 3x3, 1chip} {release: ex: S15-11-06}"
    echo ""
    exit
fi
DET=${args[0]}
REL=${args[1]}

LOCKFILE=Rsync_TinyTPV_Files_${DET}.LOCK

if [ $DET == "3x3" ];then
   # Test to see if this job is already running.
   if [ -e /tmp/${LOCKFILE} ];then
      echo "lock file /tmp/${LOCKFILE} exists.  Exiting..."
      exit
   fi
      
   touch /tmp/${LOCKFILE}

   /usr/krb5/bin/kinit -k -t /home///psihas.cron.dunegpvm01.fnal.gov.keytab psihas/cron/dunegpvm01.fnal.gov@FNAL.GOV
   
   /usr/bin/rsync -vura -e "ssh -o StrictHostKeyChecking=no" /nearline-data/OnMon/FarDet novadata@nova04.fnal.gov:/nova/data/nearline-OnMon/ --exclude '*.LOCK' --exclude '*.DONE' --exclude '*.log'
   
   rm -v /tmp/${LOCKFILE}
   exit
   
   
fi



###### for cronfile.cron # NearDet - RSync to bluearc
# */20 * * * * /home/novanearline/Nearline-test-releases/S18-01-05/Commissioning/Nearline/RsyncNearline.sh NearDet S18-01-05 > /logs/Nearline/Rsync/Rsync_$(date +\%Y-\%m-\%d_\%T).log 2>&1       
       #




