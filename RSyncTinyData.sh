#!/bin/bash
#
#    This script copies the provided LOCAL_DIRECTORY to dunegpvm (/dune/data/users/psihas/TinyTPC/Bench). A .LOCK file is created during its execution, so that simultaneous runnings are prevented.
#
#    Execution: source RSyncTinyData.sh LOCAL_DIRECTORY
#               [LOCAL_DIRECTORY should be in the following format: /Users/tinytpc/data/DATE/DATE_Hour_Minute -> the user can also upload /Users/tinytpc/data/DATE/ if they wish.]
#
#    The script checks if the directory exists, if it was created the same date as this script's execution and if it contains the "/Users/tinytpc/data/"
#
#    Created by Fernanda Psihas Olmedo.
#    Contributor: Panagiotis (Panos) Englezos
#

if [ "$#" -ne 1 ]; then
    echo "ERROR! Usage: source RSyncTinyData.sh LOCAL_DIRECTORY {/Users/tinytpc/data/DATE/DATE_Hour_Minute}"
    exit
fi

log_directory=$1
DATE_START_SCRIPT=$(date '+%Y_%m_%d')

if [ ! -d "$log_directory" ];then
   echo "ERROR! ${log_directory} does not exist."
   exit
fi
if [[ $log_directory != *"${DATE_START_SCRIPT}"* ]];then
   echo "ERROR! ${log_directory} is out of date. Today's date is ${DATE_START_SCRIPT}." # In order to avoid procrastination ;)
   exit
else
   if [[ $log_directory != *"/Users/tinytpc/data/"* ]];then
     echo "ERROR! ${log_directory} is NOT in /Users/tinytpc/data/" # Since output files are stored in /Users/tinytpc/data/.
     exit
   fi
fi

LOCKFILE=Rsync_TinyTPC_Files_${log_directory}.LOCK

# Test to see if this job is already running.
if [ -e /tmp/${LOCKFILE} ];then
    # [ -e FILE ] is "true" if FILE exists.
    echo "lock file /tmp/${LOCKFILE} exists.  Exiting..."
    exit
fi

touch /tmp/${LOCKFILE}
# /tmp/${LOCKFILE} is created. The file created using "touch" is empty. This command can be used when the user doesn’t have data to store at the time of file creation.

/usr/krb5/bin/kinit -k -t /Users/tinytpc/Code/psihas.cron.dunegpvm01.fnal.gov.keytab psihas/cron/dunegpvm01.fnal.gov@FNAL.GOV
# the "-k" option is used because it requests a ticket, obtained from a key in the local host’s keytab. The location of the keytab may be specified with the "-t" keytab_file option
# "kcroninit" creates the cron principal (<user>/cron/<host>.<domain>@FNAL.GOV) and the keytab file (/path/to/keytab/username.cron.hostname.fnal.gov.keytab).

/usr/bin/rsync -vura -e "ssh -o StrictHostKeyChecking=no" ${log_directory} psihas@dune04.fnal.gov:/dune/data/users/psihas/TinyTPC/Bench --exclude '*.LOCK' --exclude '*.DONE'
# rsync's  primary advantage over scp is for fast synchronization by only copying new or updated files.
# Options: -v, --verbose  -> increase verbosity
#          -a, --archive -> archive mode; same as -rlptgoD (no -H)
#          -r, --recursive -> recurse into directories
#          -u, --update -> skip files that are newer on the receiver
#          -e, --rsh=COMMAND -> specify the remote shell to use

rm -v /tmp/${LOCKFILE}
exit
