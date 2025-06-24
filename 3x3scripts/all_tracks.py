# all_tracks.py
# Description:
# This script is the main driver for batch processing of TinyTPC data.
# It automates the conversion of raw HDF5 files to a processed format,
# generates and uses a pedestal correction map, and then runs the
# data plotting and xy-plane track reconstruction scripts on all
# relevant data files in the current directory.

import os
import h5py
import numpy as np
import pandas as pd
import re
import glob
from tqdm import tqdm
import gc

# --- Import Custom TinyTPC Modules ---
# These scripts contain the core logic for specific processing steps.
import convert_rawhdf5_to_hdf5 # Handles the conversion from raw packet data to event-based data.
import data_plots              # Generates diagnostic plots from the processed data.
import xy_tracks                 # Performs 2D track finding in the XY plane of the detector.

# --- Pedestal File Identification ---
# Pedestal data is crucial for accurate signal measurement. It represents the
# baseline electronic noise of each channel when there is no signal.
# We first find the pedestal run file in the directory, which is expected
# to follow a specific naming pattern.
pedestal_pattern = "tile-id-3x3-pedestal_*.h5"
pedestal_files = glob.glob(pedestal_pattern)

if pedestal_files:
    pedestal_filename = pedestal_files[0] # Use the first match found.
    print(f"Using pedestal file: {pedestal_filename}")
else:
    # If no pedestal file is found, the script can't proceed accurately.
    print("Error: Pedestal HDF5 file not found. Please ensure it's in the directory.")
    # Consider adding exit() here if processing cannot continue without it.


def conv_pedestal(filename):
    """
    Calculates the mean ADC value for each channel from a pedestal file and saves it
    to a text file. This creates a pedestal map.

    The function reads the raw packet data, filters for valid data packets,
    and then maps the electronic channels (chip_id, channel_id) to a physical
    21x21 grid representing the detector's anode plane. The mean of the ADC values
    (dataword) for each channel over the duration of the run is taken as its pedestal value.

    Args:
        filename (str): The path to the input pedestal HDF5 file.
    """
    print(f"Generating pedestal map from {filename}...")

    # Open the raw HDF5 file containing pedestal data.
    with h5py.File(filename, 'r') as f:
        # Load all packets into a pandas DataFrame for efficient filtering.
        df = pd.DataFrame(f['packets'][:])

    # --- Filter for Valid Data Packets ---
    # We only care about data packets (type 0) that have passed the LArPix chip's
    # parity check (valid_parity == 1). This cleans the data.
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]

    # --- Detector Anode Plane Mapping ---
    # These arrays define the physical layout of the LArPix chips and their channels
    # on the 3x3 tile anode board. This mapping is essential to translate
    # (chip_id, channel_id) into a physical (x, y) coordinate.

    # This array maps the 64 channels of a LArPix chip to their physical layout.
    # The arrangement can seem random due to PCB routing constraints.
    channel_array = np.array([
        [28, 19, 20, 17, 13, 10,  3], [29, 26, 21, 16, 12,  5,  2],
        [30, 27, 18, 15, 11,  4,  1], [31, 32, 42, 14, 49,  0, 63],
        [33, 36, 43, 46, 50, 59, 62], [34, 37, 44, 47, 51, 58, 61],
        [35, 41, 45, 48, 53, 52, 60]
    ])

    # This array maps the 9 chips to their position in the 3x3 grid.
    chip_array = np.array([
        [14, 13, 12], [24, 23, 22], [34, 33, 32]
    ])

    # Initialize a 21x21 numpy array to store the pedestal value for each pixel.
    # The 3x3 grid of chips, each with a 7x7 channel layout, gives 21x21 total pixels.
    adc_data = np.zeros((21, 21))

    # This counter helps map the linear chip processing order to the 2D grid.
    i = 0
    # Iterate through the chips in the order defined by chip_array to build the grid row by row.
    for chip_row in chip_array:
        # The inner loops are complex; they are designed to flatten the 3D addressing
        # (chip_row, chip_col, channel_row, channel_col) into a 2D grid.
        for channel_row in channel_array:
            for chip_id in chip_row:
                # Select all packets from the current chip.
                chip_df = df.loc[df['chip_id'] == chip_id]
                for channel_idx, channel_id in enumerate(channel_row):
                    # Calculate the pixel's (x, y) coordinate in the final 21x21 grid.
                    x = i // 3
                    y = (i % 3) * 7 + channel_idx

                    # Isolate data for the specific channel.
                    channel_df = chip_df.loc[chip_df['channel_id'] == channel_id]
                    adc_values = list(channel_df['dataword'])

                    # Calculate the mean ADC value. If a channel had no hits
                    # (which is unlikely in a pedestal run), set its pedestal to 0.
                    if len(adc_values) == 0:
                        adc_data[x][y] = 0
                    else:
                        adc_data[x][y] = np.mean(adc_values)
            i += 1

    # --- Save the Pedestal Map ---
    # Extract the timestamp from the filename to create a uniquely named output file.
    regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}')
    date_str = regex.search(filename).group()
    output_pedestal_file = f'pedestal_{date_str}.txt'

    # Save the 21x21 array to a text file. This map will be loaded by other
    # analysis scripts to perform pedestal subtraction.
    np.savetxt(output_pedestal_file, adc_data, fmt='%f')
    print(f"Pedestal map saved to {output_pedestal_file}")


# --- Main Processing Logic ---

# Get a list of all files in the current directory.
all_files = os.listdir()

# --- Find and Convert Raw Data Files ---
# This loop identifies the raw data files that need to be processed.
converted_files = []
print("Searching for raw data files to convert...")
for filename in all_files:
    # We are looking for data files from the 3x3 tile, but not the pedestal file.
    if 'tile-id-3x3' in filename and 'pedestal' not in filename:
        # Process only raw files that haven't been converted yet.
        if '-raw' in filename:
            # Use regex to get the timestamp for consistent file naming.
            regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}')
            date_str = regex.search(filename).group()
            output_filename = f'tile-id-3x3_{date_str}.h5'

            # If the converted file already exists, just add it to the list to be processed.
            if output_filename in all_files:
                converted_files.append(output_filename)
            # Otherwise, run the conversion script.
            else:
                print(f"Converting {filename} -> {output_filename}...")
                # The `main` function from the conversion script is called here.
                # The `10240` is likely a buffer size or chunk size for processing.
                convert_rawhdf5_to_hdf5.main(filename, output_filename, 10240)
                converted_files.append(output_filename)

print("File conversion check complete.")

# --- Ensure Pedestal Map Exists ---
# Before running the analysis, we must have the pedestal map.
# This checks if the text file for the pedestal map was already created.
# If not, it calls the `conv_pedestal` function defined above.
regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}')
date_str = regex.search(pedestal_filename).group()
output_pedestal_file = f'pedestal_{date_str}.txt'

if output_pedestal_file not in all_files:
    conv_pedestal(pedestal_filename)
else:
    print(f"Using existing pedestal map: {output_pedestal_file}")


# --- Run Analysis on All Converted Files ---
print(f"Found {len(converted_files)} files to analyze.")
# Sorting ensures a consistent processing order, which can be useful for debugging.
converted_files = sorted(converted_files)

# Use tqdm to create a progress bar for monitoring the batch job.
for filename in tqdm(converted_files, desc="Analyzing Files"):
    print(f"\n--- Processing: {filename} ---")
    
    # Call the plotting script. This will likely generate event displays or
    # summary histograms for the current file.
    # It needs the pedestal filename to perform noise subtraction.
    data_plots.main(filename, output_pedestal_file)
    print(f"-> Diagnostic plots generated for {filename}.")

    # Call the track finding script. This is where the core physics analysis
    # of identifying particle trajectories happens.
    xy_tracks.main(filename, output_pedestal_file)
    print(f"-> XY track reconstruction complete for {filename}.")

    # --- Memory Management ---
    # Processing large HDF5 files can consume a lot of RAM.
    # `gc.collect()` explicitly tells Python to free up memory that is no longer
    # in use. This is good practice in a loop that handles large datasets
    # to prevent the system from running out of memory.
    gc.collect()

print("\nAll processing complete!")