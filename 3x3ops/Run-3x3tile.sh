#!/bin/sh
#  StartRun_TinyTPC.sh
#
#
#  Created by Fernanda Psihas Olmedo on 2/16/23.
#
#CONFIG_FILENAME='controller/network-3x3-tile-short_byhand_v18c.json'
CONFIG_FILENAME='controller/network-3x3-tile-short_byhand_v18b.json'
LOGFILE_BASE='base.log'
LOGFILE_PEDS='peds.log'
LOGFILE_THRE='thre.log'
LOGFILE_RUNS='runs.log'




echo 'Removing old files...'
cd /Users/tinytpc/GitCode/larpix-base/larpix-10x10-scripts

if [ -f "$LOGFILE_BASE" ] ; then
    rm "$LOGFILE_BASE"
fi

ls $CONFIG_FILENAME

#Python to run base.py > $LOGFILE_BASE
RUN_BASE=true
#Chech that the config loaded
echo 'Running base script.....'
while [  "$RUN_BASE" == true ]
do
  # base.py > $LOGFILE_BASE
  echo "EXEC: python3 base.py --controller_config $CONFIG_FILENAME >> /tmp/$LOGFILE_BASE  2>&1"
  python3 base.py --controller_config $CONFIG_FILENAME >> /tmp/$LOGFILE_BASE  2>&1
  echo '---'

  if [ "$(sed '9q;d' /tmp/${LOGFILE_BASE})" = '[FINISH BASE]' ];then
    echo '---   ---   ---   ---   ---   ---'
    echo 'Loading congig ..... SUCCESS!'
    echo '---   ---   ---   ---   ---   ---'
    RUN_BASE=false
  else
    sed '4q;d' /tmp/${LOGFILE_BASE}
    sed '5q;d' /tmp/${LOGFILE_BASE}
    sed '9q;d' /tmp/${LOGFILE_BASE}
    sed '13q;d' /tmp/${LOGFILE_BASE}

    echo 'Running base script unsuccessfull. Trying again.'
    rm /tmp/$LOGFILE_BASE
  fi
done
#
echo '---   ---   ---   ---   ---   ---'
echo 'Moving on to pedestal run'
echo '---   ---   ---   ---   ---   ---'
#
echo 'Removing old files...'
cd /Users/tinytpc/GitCode/larpix-base/larpix-10x10-scripts

if [ -f "$LOGFILE_PEDS" ] ; then
    rm "$LOGFILE_PEDS"
fi

#Python to run base.py > $LOGFILE_BASE
RUN_PEDS=true
#Chech that the config loaded
echo 'Running base script.....'
while [  "$RUN_PEDS" == true ]
do
  # base.py > $LOGFILE_PEDS
  echo "EXEC: python3 pedestal_qc.py --controller_config ${CONFIG_FILENAME}"
  python3 pedestal_qc.py --controller_config ${CONFIG_FILENAME} >> /tmp/$LOGFILE_PEDS  2>&1
  echo '---'
  sed '13q;d' /tmp/${LOGFILE_PEDS}
  # echo '---'
  # cat /tmp/${LOGFILE_PEDS}
  if [ "$(sed '13q;d' /tmp/${LOGFILE_PEDS})" = '[FINISH BASE]' ];then
    echo '---   ---   ---   ---   ---   ---'
    echo 'Loading congig ..... SUCCESS!'
    echo '---   ---   ---   ---   ---   ---'
    RUN_PEDS=false
  else
    sed '13q;d' /tmp/${LOGFILE_PEDS}
    echo 'Running base script unsuccessfull. Trying again.'
    rm /tmp/$LOGFILE_PEDS
  fi
done

echo '---   ---'
DATE=$(date +%Y_%m_%d)

DISABLED_FILE="$(ls -t /Users/tinytpc/data/${DATE}/tile-id-tile-pedestal-disabled-list*.json | head -n 1)"
PEDESTAL_FILE="$(ls -t /Users/tinytpc/data/${DATE}/tile-id-tile-pedestal_*disabled-channels.h5| head -n 1)"
echo 'Found disabled list file ... '
echo $DISABLED_FILE
echo 'Found pedestal file ... '
echo $PEDESTAL_FILE


#python3 threshold_qc.py --controller_config ${CONFIG_FILENAME} --disabled_list /Users/tinytpc/data/2023_04_20/tile-id-tile-pedestal-disabled-list-2023_04_20_14_10_20_CDT-v1.0.3.json --pedestal_file /Users/tinytpc/data/2023_04_20/tile-id-tile-pedestal_2023_04_20_14_09_10_CDT-default-disabled-channels.h5

echo 'Script in progress... do this next, I think.. '

#this works to do make loop
echo "EXEC: python3 threshold_qc.py --controller_config ${CONFIG_FILENAME} --disabled_list ${DISABLED_FILE}  --pedestal_file ${PEDESTAL_FILE}"

# then start run like this
# CONFIG_DIR=configs/${DATE}
# mkdir ${CONFIG_DIR}
# mv configs/tile-id-tile-config-1-*${DATE} ${CONFIG_DIR}/.
#
# python3 start_run_log_raw.py --config_name ${CONFIG_DIR} --controller_config ${CONFIG_FILENAME} --outdir /Users/tinytpc/data/${DATE} --runtime 60
#




#
#
# /Users/tinytpc/data/2023_02_20/tile-id-tile-pedestal_2023_02_20_13_19_40_CST-default-disabled-channelsconfig.json
# Found disabled list file ...
# /Users/tinytpc/data/2023_02_20/tile-id-tile-pedestal-disabled-list-2023_02_20_19_14_22_CST-v1.0.3.json
