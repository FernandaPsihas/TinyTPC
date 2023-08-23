#!/bin/sh
#
# This bash file runs our whole sequnce of scripts automatically (making sure that they were successful). The log files are
# being stored to /tinytpc/data/
#
# Execution: ./Run-3x3tile.sh base_flag pedestal_flag threshold_flag different_pedestal_files_flag start_run_flag different_config_files_flag copy_to_dune_flag
#
# Created by Fernanda Psihas Olmedo on 2/16/23.
# Main-Contributor / Co-Author: Panagiotis (Panos) Englezos
#######################################################################

#!/bin/sh

#<<<<<<< HEAD
##Date and Time when the bash script starts running
#DATE_HOUR_START_SCRIPT=$(date '+%Y_%m_%d_%H_CT')
#DATE_TIME_START_SCRIPT=$(date '+%Y_%m_%d_%H-%M_CT')
#DATE_SECONDS_START_SCRIPT=$(date '+%Y_%m_%d_%H-%M-%S_CT')
#DATE_START_SCRIPT=$(date '+%Y_%m_%d')

#if [ "$#" -ne 4 ]; then
#    printf 'ERROR! You must provide four (4) and only four booleans ("true" or "false")!'
#Verify that all four flags have input values.
DATE_START_SCRIPT=$(date '+%Y_%m_%d')

if [ "$#" -ne 6 ]; then
    printf 'ERROR! You must provide six and only six booleans ("true" or "false")!'
    exit 1
fi

#Verify that each flag is either "true" or "false", as the boolean flags are case-sensitive.
for input in "$@"
do
  if [ "$input" != true ] && [ "$input" != false ]; then
      printf 'ERROR! You must provide either "true" or "false"!\n'
      exit 1
  fi
done

#<<<<<<< HEAD
#if [ "$2" = true ]; then #the user wants to execute pedestal_qc.py
#  echo "\nShould any keywords be appended to the name of the output pedestal files? (y/n)"
#  read APP_KEYW
#  if [ "$APP_KEYW" != "y" ] && [ "$APP_KEYW" != "n" ]; then
#      printf 'ERROR! You must provide either "y" or "n"!'
#      exit 1
#  fi
#  if [ "$APP_KEYW" = "y" ]; then
#    echo "\nWhich keywords should be included (make sure to include the pedestal's cut values)?"
#    read KEYW
#  fi
#fi

#dif_ped_files=false
#if [ "$3" = true ] && [ "$2" = false ]; then #the user wants to execute threshold_qc.py, but not pedestal_qc.py#  (so, there are no default output pedestal files)
#  dif_ped_files=true
#=======
if [ "$4" = true ]; then

  #Verify that the input files are not empty and in the correct format.
  non_empty_file1=false
  non_empty_file2=false
  correct_file_format_json=false
  correct_file_format_h5=false
  file1_exists=false
  file2_exists=false
  while [[ "$file1_exists" = false || "$file2_exists" = false || "$non_empty_file1" = false || "$non_empty_file2" = false || "$correct_file_format_json" = false || "$correct_file_format_h5" = false ]]
  do
    echo "\nProvide the two pedestal files that will be used as input parameters for threshold_qc.py:"
    read DISABLED_FILE PEDESTAL_FILE
    if [ ! -z "$DISABLED_FILE" ];then
        non_empty_file1=true
        if [[ $DISABLED_FILE == *".json"*  ]];then
            correct_file_format_json=true
          else
              echo "\nERROR! The first entry should be a .json file"
              continue
          fi
          if [ -f "$DISABLED_FILE" ]; then
              file1_exists=true
          else
            echo "\nERROR! The first entry doesn't exist. Please provide its full path."
            continue
          fi
    else
        echo "\nERROR! Provide two and only two files"
        continue
    fi
    if [[ $DISABLED_FILE != *"${DATE_START_SCRIPT}"* ]];then
       echo "\n${DISABLED_FILE} is out of date. Today's date is ${DATE_START_SCRIPT}."
       continue
    fi
    if [ ! -z "$PEDESTAL_FILE" ]; then
        non_empty_file2=true
        if [[ $PEDESTAL_FILE == *".h5"* ]]; then
            correct_file_format_h5=true
        else
            echo "\nERROR! The second entry should be a .h5 file"
            continue
        fi
        if [ -f "$PEDESTAL_FILE" ]; then
            file2_exists=true
        else
          echo "\nERROR! The second entry doesn't exist. Please provide its full path."
          continue
        fi
    else
        echo "\nERROR! Provide two and only two files"
        continue
    fi
    if [[ $PEDESTAL_FILE != *"${DATE_START_SCRIPT}"* ]];then
       echo "\n${PEDESTAL_FILE} is out of date. Today's date is ${DATE_START_SCRIPT}."
       continue
    fi
  done
fi

#<<<<<<< HEAD
#if [ "$3" = true ]; then #the user wants to execute threshold_qc.py
#  echo "\nShould any keywords be appended to the name of the output threshold files? (y/n)"
#  read APP_KEYW_THR
#  if [ "$APP_KEYW_THR" != "y" ] && [ "$APP_KEYW_THR" != "n" ]; then
#      printf 'ERROR! You must provide either "y" or "n"!\n'
#      exit 1
#  fi
#  if [ "$APP_KEYW_THR" = "y" ]; then
#    echo "\nWhich keywords should be included (make sure to include the pedestal's cut values)?"
#    read KEYW_THR
#  fi
#fi
#
dif_thresh_files=false
if [ "$4" = true ] && [ "$3" = false ]; then #the user wants to execute start_run_log_raw.py, but not threshold_qc.py  (so, there are no default output threshold_qc files)
  dif_thresh_files=true

if [ "$6" = true ]; then
  #Verify that the input files are not empty and in .json format.
  while :
  do
    echo "\nProvide the directory where the nine (9) configuration files that will be used as input parameters for start_run_log_raw.py, are stored:"
    read DIRECTORY
    input_config_files=( $DIRECTORY* )
    if [ ${#input_config_files[@]} -ne 9 ]; then
      echo "\nERROR! Not a directory with exactly 9 files was provided. Verify that the provided path ENDS i"
      echo "\nERROR! Not exactly 9 files were provided. Verify that the provided path ends in "/" "
      continue
    fi
    i_file=1;
    declare -a chip_ids_array=(12 13 14 22 23 24 32 33 34)
    for FILE in "${input_config_files[@]}";
      do
        echo "${FILE}"
        if [ ! -f "$FILE" ];then
           echo "ERROR! ${FILE} does not exist (make sure to provide its full path)."
           break
        fi
        if [[ $FILE != *".json"* ]];then
           echo "ERROR! ${FILE} 's format is NOT .json !"
           break
        fi
        if [[ $FILE != *"${DATE_START_SCRIPT}"* ]];then
           echo "${FILE} is out of date. Today's date is ${DATE_START_SCRIPT}."
           break
        fi
        file="${FILE%-*}"
        file="${file##*-}"
        chip_ids_array=( "${chip_ids_array[@]/$file}" )
        i_file=$((i_file + 1))
    done
    if [ $i_file -ne 10 ]; then
      continue
    else
      i_chip_id=1;
      for CHIP_ID in "${chip_ids_array[@]}";
      do
        if [ "${CHIP_ID}" != "" ]; then
          echo "\nERROR! Same chip id configuration file was used. Chip ${CHIP_ID}'s file was not provided."
          continue
        else
          i_chip_id=$((i_chip_id + 1))
        fi
      done
      if [ $i_chip_id -ne 9 ]; then
        break
      fi
    fi
  done
fi

RUN_BASE=$1
RUN_PEDESTAL_FINBASE=$2
RUN_THRESHOLD=$3

DIFFERENT_PEDESTAL_FILES_FLAG=$4
RUN_START_RUN=$5
DIFFERENT_CONFIG_FILES_FLAG=$6

#Date and Time when the bash script starts running
DATE_HOUR_START_SCRIPT=$(date '+%Y_%m_%d_%H_CT')
DATE_TIME_START_SCRIPT=$(date '+%Y_%m_%d_%H-%M_CT')
DATE_SECONDS_START_SCRIPT=$(date '+%Y_%m_%d_%H-%M-%S_CT')

#Go to the directory where we want to store our data and create a folder based on the date and time of the current execution
#we are storing based on minutes and not seconds, because that would be too specific.
cd /Users/tinytpc/data/

if [ ! -d "$DATE_START_SCRIPT" ]; then
  mkdir -p ./${DATE_START_SCRIPT}
fi

cd ./${DATE_START_SCRIPT}
mkdir -p ./${DATE_TIME_START_SCRIPT}
log_directory="/Users/tinytpc/data/${DATE_START_SCRIPT}/${DATE_TIME_START_SCRIPT}/"
echo "\nDirectory of logfiles: /Users/tinytpc/data/${DATE_START_SCRIPT}/${DATE_TIME_START_SCRIPT} \n"

#Go to the directory where our scripts are.
cd /Users/tinytpc/GitCode/larpix-base/larpix-10x10-scripts

CONFIG_FILENAME='./controller/network-3x3-tile-short_byhand_v18b.json' # network configuration of the LArPix chips
if [ -f "$CONFIG_FILENAME" ]; then
    file1_exists=true
else
  echo "\nERROR! The first entry doesn't exist. Please provide its full path."
  continue
fi


if [  "$RUN_BASE" = false ];then
  echo "The execution of base.py will be skipped."
else
  echo "Now executing base.py: python3 base.py --controller_config $CONFIG_FILENAME >> ./base.log  2>&1 \n"
fi

i_base=1;
while [  "$RUN_BASE" = true ]
do
  #Date and Time when base.py startes running
  DATE_TIME_BASE_START=$(date +"%Y_%m_%d_%H-%M_CT")
  DATE_SECONDS_BASE_START=$(date +"%S")

  echo "\n------ Attempt: $i_base ------"

  python3 base.py --controller_config $CONFIG_FILENAME >> ./base.log  2>&1

  if [ "$(sed '9q;d' base.log)" = '[FINISH BASE]' ];then
    echo '\nSuccess! \n'
    DATE_TIME_BASE_END=$(date +"%Y_%m_%d_%H-%M_CT")
    DATE_SECONDS_BASE_END=$(date +"%S")
    DURATION=$((DATE_SECONDS_BASE_END - DATE_SECONDS_BASE_START))
    echo "\nAttempt $i_base ran for $DURATION seconds"
    echo "This attempt ran for $DURATION seconds" >> base.log
    mv base.log successful_base_attempt_${i_base}_${DATE_TIME_BASE_START}.log #rename the base file based on the run's information
    mv successful_base_attempt_${i_base}_${DATE_TIME_BASE_START}.log ${log_directory} #move the file to the log directory
    RUN_BASE=false
  else
    DATE_TIME_BASE_END=$(date +"%Y_%m_%d_%H-%M_CT")
    DATE_SECONDS_BASE_END=$(date +"%S")
    DURATION=$((DATE_SECONDS_BASE_END - DATE_SECONDS_BASE_START))
    echo "\nAttempt $i_base ran for $DURATION seconds"
    echo "This attempt ran for $DURATION seconds" >> base.log
    mv base.log failed_base_attempt_${i_base}_${DATE_TIME_BASE_START}.log #rename the base file based on the run's information
    mv failed_base_attempt_${i_base}_${DATE_TIME_BASE_START}.log ${log_directory} #move the file to the log directory
    i_base=$((i_base + 1))
    echo '\nFailure! Trying again...'
  fi

done
echo '\n------------------------\n '

if [  "$RUN_PEDESTAL_FINBASE" = false ];then
  echo "The execution of pedestal_qc.py will be skipped."
else
  echo "Now executing pedestal_qc.py: python3 pedestal_qc.py --controller_config $CONFIG_FILENAME >> ./pedestal.log  2>&1 \n"
fi

i_pedestal=0;

while [  "$RUN_PEDESTAL_FINBASE" = true ]
#Execute pedestal_qc.py until both conditions are satisfied:
#  1) It contains "[FINISH BASE]" in the 13th lines
#  2) It doesn't contain "RuntimeError" (since the number of disabled channels can vary per run, we require that
#  it does't exist in the whole file).
do
  i_pedestal=$((i_pedestal + 1))
  #Date and Time when pedestal_qc.py starts running
  DATE_TIME_PEDESTAL_START=$(date +"%Y_%m_%d_%H-%M_CT")
  DATE_SECONDS_PEDESTAL_START=$(date +"%S")

  echo "\n------ Attempt: $i_pedestal ------"
  python3 pedestal_qc.py --controller_config ${CONFIG_FILENAME} >> pedestal.log  2>&1

  if [ "$(sed '13q;d' pedestal.log)" = '[FINISH BASE]' ];then
    echo '\nSuccess! \n'
    DATE_TIME_PEDESTAL_END=$(date +"%Y_%m_%d_%H-%M_CT")
    DATE_SECONDS_PEDESTAL_END=$(date +"%S")
    DURATION=$((DATE_SECONDS_PEDESTAL_END - DATE_SECONDS_PEDESTAL_START))

   #Possible monitoring flags:
        # 1) Value of VDDD and VDDA (given the number of data, this can be updated to be a flag for bad events.)
        # 2) Number of bad channels
    grep -E "VDDD|VDDA" "pedestal.log" #This line will print the values of VDDD, VDDA, IDDD, IDDA
    grep -E "===========" "pedestal.log" #This line will print the number of bad channels

    echo "\nAttempt $i_pedestal ran for $DURATION seconds"
    echo "This attempt ran for $DURATION seconds" >> pedestal.log
    mv pedestal.log successful_pedestal_attempt_${i_pedestal}_${DATE_TIME_PEDESTAL_START}.log #rename the pedestal file based on the run's information
    mv successful_pedestal_attempt_${i_pedestal}_${DATE_TIME_PEDESTAL_START}.log ${log_directory} #move the file to the log directory
    RUN_PEDESTAL_FINBASE=false
  else
    DATE_TIME_PEDESTAL_END=$(date +"%Y_%m_%d_%H-%M_CT")
    DATE_SECONDS_PEDESTAL_END=$(date +"%S")
    DURATION=$((DATE_SECONDS_PEDESTAL_END - DATE_SECONDS_PEDESTAL_START))
    echo "\nAttempt $i_pedestal ran for $DURATION seconds"
    echo "This attempt ran for $DURATION seconds" >> pedestal.log
    mv pedestal.log failed_pedestal_attempt_${i_pedestal}_${DATE_TIME_PEDESTAL_START}.log #rename the pedestal file based on the run's information
    mv failed_pedestal_attempt_${i_pedestal}_${DATE_TIME_PEDESTAL_START}.log ${log_directory} #move the file to the log directory
    echo '\nFailure! Trying again...'
  fi
  done

  if (( $i_pedestal > 0 )); then

    search_dir=/Users/tinytpc/data/${DATE_START_SCRIPT}
    for entry_json in "$search_dir"/*.json
    do
        echo "${entry_json} is moved to ${log_directory}"
        mv ${entry_json} ${log_directory}
    done
    for entry_h5 in "$search_dir"/*.h5
    do
        echo "${entry_h5} is moved to ${log_directory}"
        mv ${entry_h5} ${log_directory}
    done
    for entry_recur in "$search_dir"/tile-id-tile-recursive-pedestal*
    do
        echo "${entry_recur} is moved to ${log_directory}"
        mv ${entry_recur} ${log_directory}
    done
  fi

echo '\n------------------------\n '

# If input flag was false, then, by default, threshold_qc.py will use the most recent pedestal files.
if [  "$RUN_THRESHOLD" = false ];then
  echo "The execution of threshold_qc.py will be skipped."
else
  if [ "$DIFFERENT_PEDESTAL_FILES_FLAG" = false && "$RUN_PEDESTAL_FINBASE" = true ]; then
    DISABLED_FILE="$(ls -t ${log_directory}tile-id-tile-pedestal-disabled-list*.json | head -n 1)"
    PEDESTAL_FILE="$(ls -t ${log_directory}tile-id-tile-pedestal_*disabled-channels.h5| head -n 1)"

    echo "The most recent disabled list and default disabled channels are: \n${DISABLED_FILE}\n${PEDESTAL_FILE}"
  else
    echo "As requested, the following files will be used as input parameters for threshold_qc.py: \n${DISABLED_FILE}\n${PEDESTAL_FILE}"
  fi
  echo "\nNow executing threshold_qc.py: python3 threshold_qc.py --controller_config $CONFIG_FILENAME --disabled_list ${DISABLED_FILE}  --pedestal_file ${PEDESTAL_FILE} >> ./threshold.log  2>&1 \n"
fi

i_threshold=0;

while [  "$RUN_THRESHOLD" = true ]
do
  i_threshold=$((i_threshold + 1))
  #Date and Time when threshold_qc.py starts running
  DATE_TIME_THRESHOLD_START=$(date +"%Y_%m_%d_%H-%M_CT")
  DATE_SECONDS_THRESHOLD_START=$(date +"%S")

  echo "\n------ Attempt: $i_threshold ------"
  python3 threshold_qc.py --controller_config ${CONFIG_FILENAME} --disabled_list ${DISABLED_FILE}  --pedestal_file ${PEDESTAL_FILE} >> threshold.log  2>&1

  if [ "$(sed '9q;d' threshold.log)" = '[FINISH BASE]' ];then
    echo '\nSuccess! \n'
    DATE_TIME_THRESHOLD_END=$(date +"%Y_%m_%d_%H-%M_CT")
    DATE_SECONDS_THRESHOLD_END=$(date +"%S")
    DURATION=$((DATE_SECONDS_THRESHOLD_END - DATE_SECONDS_THRESHOLD_START))

    echo "\nAttempt $i_threshold ran for $DURATION seconds"
    echo "This attempt ran for $DURATION seconds" >> threshold.log
    mv threshold.log successful_threshold_attempt_${i_threshold}_${DATE_TIME_THRESHOLD_START}.log #rename the threshold file based on the run's information
    mv successful_threshold_attempt_${i_threshold}_${DATE_TIME_THRESHOLD_START}.log ${log_directory} #move the file to the log directory
    RUN_THRESHOLD=false
  else
    DATE_TIME_THRESHOLD_END=$(date +"%Y_%m_%d_%H-%M_CT")
    DATE_SECONDS_THRESHOLD_END=$(date +"%S")
    DURATION=$((DATE_SECONDS_THRESHOLD_END - DATE_SECONDS_THRESHOLD_START))
    echo "\nAttempt $i_threshold ran for $DURATION seconds"
    echo "This attempt ran for $DURATION seconds" >> threshold.log
    mv threshold.log failed_threshold_attempt_${i_threshold}_${DATE_TIME_THRESHOLD_START}.log #rename the threshold file based on the run's information
    mv failed_threshold_attempt_${i_threshold}_${DATE_TIME_THRESHOLD_START}.log ${log_directory} #move the file to the log directory
    echo '\nFailure! Trying again...'
  fi
  done

  if (( $i_threshold > 0 )); then
    for i in {1..9}
    do
     CHIP_FILE="$(ls -t ./tile-id-tile-config-1-*.json | head -n 1)"
     echo "${CHIP_FILE}"
     mkdir -p ${log_directory}/configs
     mv ${CHIP_FILE} ${log_directory}/configs
   done
  fi

  if [ "$dif_thresh_files" = false ]; then
    DIRECTORY=${log_directory}configs/
=======
  if [[ "$DIFFERENT_CONFIG_FILES_FLAG" = false && "$RUN_THRESHOLD" = true ]]; then
    DIRECTORY=${log_directory}/configs
  fi
echo '\n------------------------\n '

if [  "$RUN_START_RUN" = false ];then
  echo "The execution of start_run_log_raw.py will be skipped."
else
  echo "\nNow executing start_run_log_raw.py: python3 start_run_log_raw.py --config_name ${DIRECTORY} --controller_config ${CONFIG_FILENAME} --outdir ${log_directory} --runtime 60 >> start.log  2>&1"
fi

i_start=0;

while [  "$RUN_START_RUN" = true ]
do
  i_start=$((i_start + 1))
  #Date and Time when start_run_log_raw.py starts running
  DATE_TIME_RUN_START=$(date +"%Y_%m_%d_%H-%M_CT")
  DATE_SECONDS_RUN_START=$(date +"%S")

  echo "\n------ Attempt: $i_start ------"
  python3 start_run_log_raw.py --config_name ${DIRECTORY} --controller_config ${CONFIG_FILENAME} --outdir ${log_directory} --runtime 60 >> start.log  2>&1

  if [ "$(sed '9q;d' start.log)" = '[FINISH BASE]' ];then
    echo '\nSuccess! \n'
    DATE_TIME_RUN_END=$(date +"%Y_%m_%d_%H-%M_CT")
    DATE_SECONDS_RUN_END=$(date +"%S")
    DURATION=$((DATE_SECONDS_RUN_END - DATE_SECONDS_RUN_START))

    echo "\nAttempt $i_start ran for $DURATION seconds"
    echo "This attempt ran for $DURATION seconds" >> start.log
    mv start.log successful_start_attempt_${i_start}_${DATE_TIME_RUN_START}.log #rename the start_run file based on the run's information
    mv successful_start_attempt_${i_start}_${DATE_TIME_RUN_START}.log ${log_directory} #move the file to the log directory
    RUN_START_RUN=false
  else
    DATE_TIME_RUN_END=$(date +"%Y_%m_%d_%H-%M_CT")
    DATE_SECONDS_RUN_END=$(date +"%S")
    DURATION=$((DATE_SECONDS_RUN_END - DATE_SECONDS_RUN_START))
    echo "\nAttempt $i_threshold ran for $DURATION seconds"
    echo "This attempt ran for $DURATION seconds" >> start.log
    sed '13q;d'  start.log
    mv start.log failed_start_attempt_${i_start}_${DATE_TIME_RUN_START}.log #rename the start_run file based on the run's information
    mv failed_start_attempt_${i_start}_${DATE_TIME_RUN_START}.log ${log_directory} #move the file to the log directory
    echo '\nFailure! Trying again...'
  fi
done

echo '\n------------------------'
