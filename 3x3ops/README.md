# 3x3 Operations Scripts

This program is executed the following way: ./Run-3x3tile.sh base_flag pedestal_flag threshold_flag different_pedestal_files_flag start_run_flag different_config_files_flag [either "true" or "false"]
- base_flag indicates to the program if base.py should be executed.
- pedestal_flag indicates to the program if pedestal_qc.py should be executed.
- threshold_flag indicates to the program if threshold_qc.py should be executed.
- different_pedestal_files_flag indicates to the program if the input files for threshold_qc.py will be the most recent ones (this requires that pedestal_flag is true also) or will be provided by the user.
- start_run_flag indicates to the program if start_run_log_raw.py should be executed.
- different_config_files_flag indicates to the program if the input directory for start_run_log_raw.py will be the most recent one (this requires that threshold_flag is true also) or will be provided by the user.


All flags need to have a value before the script can be executed successfully.Script execution will repeat until the respective script has been successfully completed.  The program creates the following directory in order to store the output files: /tinytpc/data/DATE/DATE_Hour_Minute (the time is based on when the program began its execution) [this is the local_directory].

Each of the four (4) scripts, when it is executed, a log file is created for every attempt (successful or not) which contain in its title the result (success or failure), the attempt's number and the date and time (hours:minutes:seconds) when the specific script began. In the log file, besides the terminal logs, the duration of the attempt is also stored.
All output files of these scripts are stored in the local_directory. More specifically, since start_run_log_raw.py requires a directory as input, the output files of threshold_qc.py are stored in local_directory/configs.


Regarding the user inputs [they should be provided with their full path], the program checks if they exist locally, if they are in the right format (.json and .h5 for the threshold_qc.py inputs and .json for the start_run_log_raw.py inputs) and the same date as the program's execution. Additionally, for the start_run_log_raw.py inputs checks if a configuration file has been submitted for each chip id.


test(https).
test(submission via workstation mac)
