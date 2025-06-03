#!/bin/bash

# run kinit auth b4 running this

# Define variables for whoever is using the script
LOCAL_BASE_DIR="/Users/tinytpc/hannah2_test_data"
REMOTE_BASE_DIR="/exp/dune/data/users/englezos/TinyTPC_Fernanda/Bench/hannah2_testing"
REMOTE_HOSTNAME="dunegpvm07.fnal.gov"
USERNAME="hmccrigh"

while true; do
    # Find folders with "2024_07" in the name and modified in the last 24 hours
    FOLDERS=$(find "$LOCAL_BASE_DIR" -maxdepth 1 -mindepth 1 -type d -mtime -1 -name '*2024_07*')

    # Loop through each folder
    for LOCAL_PATH in $FOLDERS; do
        FOLDER=$(basename "$LOCAL_PATH")
        REMOTE_PATH="$REMOTE_BASE_DIR/$FOLDER"

        # Convert files and run data_plots.py on each converted file
        RAW_FILES=$(find "${LOCAL_PATH}" -name '*tile-id-3x3-raw*.h5')
        for RAW_FILE in $RAW_FILES; do
            data_rawfilepath=$RAW_FILE
            data_rawfilename=$(basename "$data_rawfilepath")
            data_directory=$(dirname "$data_rawfilepath")
            data_filename=$(echo "$data_rawfilename" | sed 's/-raw//')
            output_filepath="${data_directory}/tile-id-3x3-${data_filename}"
            blocksize="10240"

            echo "Data Filename: $output_filepath"
            echo "Raw Filepath: ${data_rawfilepath}"
            if [ ! -f "$output_filepath" ]; then
                echo 'Converting file...'
                python3 /Users/tinytpc/GitCode/TinyTPC/3x3scripts/convert_rawhdf5_to_hdf5.py --input_filename "$data_rawfilepath" --output_filename "$output_filepath" --block_size "$blocksize"
            fi

            # Run data_plots.py on the converted file
            if [ -f "$output_filepath" ]; then
                echo "Running data_plots.py on $output_filepath..."
                python3 /Users/tinytpc/GitCode/TinyTPC/3x3scripts/data_plots.py --filename "$output_filepath"
                echo "data_plots.py completed."
            else
                echo "Converted file $output_filepath not found."
            fi
        done

        # Transfer files to the remote computer
        if [ -d "$LOCAL_PATH" ]; then
            echo "Transferring $LOCAL_PATH to $USERNAME@$REMOTE_HOSTNAME:$REMOTE_PATH"
            scp -r -o GSSAPIAuthentication=yes "$LOCAL_PATH" "$USERNAME@$REMOTE_HOSTNAME:$REMOTE_PATH"

            if [ $? -eq 0 ]; then
                echo "Successfully transferred $FOLDER"
            else
                echo "Failed to transfer $FOLDER"
            fi
        else
            echo "Directory $LOCAL_PATH does not exist"
        fi
    done

    # Sleep for a little less than 24 hours before running again
    sleep 86000
done

