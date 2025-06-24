# xy_tracks.py
# Description:
# This script analyzes a processed TinyTPC data file to identify and visualize
# candidate particle tracks. It scans the data for time windows with a high
# number of hits. For each candidate event, it generates a detailed, multi-panel
# plot showing the 2D track projection (XY plane) and other diagnostic information.
# All plots from a single run are saved into one PDF file.

import matplotlib.pyplot as plt
import pandas as pd
import h5py
import numpy as np
import argparse
import seaborn as sns
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages
import os
import re

# --- Physics Constants and Drift Velocity Calculation ---
# To reconstruct the Z-coordinate of a hit, we need to know how fast electrons
# drift in the liquid argon. This velocity depends on the electric field (E) and
# the temperature (T). This calculation uses the Walkowiak model for mobility.

# --- Detector and Run Parameters ---
V = 4      # Applied voltage in kV
d = 15     # Drift distance (cathode to anode) in cm
T = 90     # Approximate LAr temperature in Kelvin
T_0 = 89   # Reference temperature for the model in Kelvin

# --- Electric Field Calculation ---
E = V / d  # E-field in kV/cm

# --- Walkowiak Model Parameters for Electron Mobility (mu) in LAr ---
# These empirical constants are derived from experimental measurements.
a_0 = 551.6
a_1 = 7158.3
a_2 = 4440.43
a_3 = 4.29
a_4 = 43.63
a_5 = 0.2053

# --- Electron Drift Velocity Calculation ---
# Mobility (mu) describes how easily electrons move through a medium under an E-field.
mu_formula = (a_0 + a_1*E + a_2*E**(3/2) + a_3*E**(5/2)) / (1 + (a_1/a_0)*E + a_4*E**2 + a_5*E**3)
mu = mu_formula * (T/T_0)**(-3/2)  # Mobility in cm^2/V/s

# Drift velocity (v) is mobility times the electric field.
# The factor of 1000 converts E from kV/cm to V/cm.
v = mu * E * 1000  # Drift velocity in cm/s

# Total time for an electron to cross the entire detector.
# The factor of 1e7 converts the time from seconds to 0.1 microsecond "ticks",
# which is the native time unit of the LArPix clock (10 MHz).
drift_time = (d / v) * 1e7
# print(f"Calculated drift velocity: {v:.2f} cm/s")
# print(f"Maximum drift time: {drift_time:.2f} [0.1 us ticks]")


def parse_pedestal(filename):
    """
    DEPRECATED/REDUNDANT: This function appears to recalculate the pedestal map from a raw
    pedestal file. In the main workflow (`all_tracks.py`), a pedestal TEXT FILE is
    already created. This function should ideally be replaced by loading that .txt file
    (e.g., using np.loadtxt) for efficiency.

    For now, it reads the raw pedestal HDF5 file and computes the mean ADC value
    for each channel, returning it as a 21x21 numpy array.
    """
    # This function is nearly identical to conv_pedestal in all_tracks.py
    # It is recommended to have one canonical pedestal generation script and
    # have analysis scripts load the resulting text file.
    with h5py.File(filename, 'r') as f:
        df = pd.DataFrame(f['packets'][:])
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]

    channel_array = np.array([[28, 19, 20, 17, 13, 10,  3], [29, 26, 21, 16, 12,  5,  2],
                              [30, 27, 18, 15, 11,  4,  1], [31, 32, 42, 14, 49,  0, 63],
                              [33, 36, 43, 46, 50, 59, 62], [34, 37, 44, 47, 51, 58, 61],
                              [35, 41, 45, 48, 53, 52, 60]])
    chip_array = np.array([[14, 13, 12], [24, 23, 22], [34, 33, 32]])

    adc_data = np.zeros((21, 21)) # Use np.zeros for clarity over np.arange.reshape
    i = 0
    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                chip = df.loc[df['chip_id'] == chip_id]
                for channel_id in range(len(channel_lst)):
                    x = i // 3
                    y = (i * 7) % 21 + channel_id
                    channel = chip.loc[chip['channel_id'] == channel_lst[channel_id]]
                    adc = list(channel['dataword'])
                    if len(adc) == 0:
                        adc_data[x][y] = 0
                    else:
                        adc_data[x][y] = np.mean(adc)
            i += 1
    return adc_data


def parse_file(filename):
    """
    Reads a processed (event-built) HDF5 data file and loads the valid data
    packets into a pandas DataFrame. Extracts the run date from the filename.
    """
    with h5py.File(filename, 'r') as f:
        df = pd.DataFrame(f['packets'][:])
    
    # Filter for valid data packets.
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]
    
    # Extract timestamp from filename for titling plots.
    regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}') 
    date = regex.search(filename).group()
    return df, date


def parse_json(json_filename):
    """Helper function to extract the channel mask list from a LArPix configuration file."""
    with open(json_filename) as f:
        off = []
        for line in f:
            if 'channel_mask' in line:
                # This is a bit fragile; it just grabs all 0s and 1s.
                # A more robust method would be to parse the JSON format correctly.
                for char in line:
                    if char in ('1', '0'):
                        off.append(int(char))
    return off


def channel_mask():
    """
    Reads all LArPix JSON configuration files in the '/configs' subdirectory to
    determine which channels were disabled ('masked') during the run.

    Returns:
        d (dict): A dictionary mapping chip_id (str) to its 64-element channel mask list.
    """
    path = os.path.dirname(os.path.realpath(__file__))
    j_dir = os.path.join(path, 'configs') # Use os.path.join for cross-platform compatibility.

    d = {}
    if not os.path.isdir(j_dir):
        print(f"Warning: Config directory not found at {j_dir}")
        return d

    # Temporarily change directory to read configs
    original_dir = os.getcwd()
    os.chdir(j_dir)
    files = os.listdir()
    for file in files:
        if file.endswith('.json'):
            # This regex assumes a '1-1-12' style name format.
            regex = re.compile(r'\d{1}-\d{1}-(\d{2})')
            match = regex.search(file)
            if match:
                chip_id = match.group(1) # Group 1 is just the chip number
                d[chip_id] = parse_json(file)
    os.chdir(original_dir) # Change back to the original directory
    return d


def plot_xy_selected(df, start_time, end_time, pedestal, date=''):
    """
    Generates a comprehensive multi-panel plot for a single candidate track event.
    """
    # --- Figure and Subplot Setup ---
    # Using gridspec allows for creating a complex layout with different subplot sizes.
    fig = plt.figure(figsize=(9, 11))
    spec = fig.add_gridspec(3, 2)
    ax0 = fig.add_subplot(spec[0, 0]) # Top-left: ADC heatmap
    ax1 = fig.add_subplot(spec[0, 1]) # Top-right: Time heatmap
    ax2 = fig.add_subplot(spec[1, :]) # Middle, full-width: ADC vs. Time
    ax3 = fig.add_subplot(spec[2, 0]) # Bottom-left: ADC histogram
    ax4 = fig.add_subplot(spec[2, 1]) # Bottom-right: Time histogram
    fig.set_tight_layout(True)
    ax = [ax0, ax1, ax2, ax3, ax4]

    # --- Data Filtering and Plot Titling ---
    # Isolate the data to the specific time window for this event.
    min_global_time = min(df['timestamp'])
    df_cut = df[(df['timestamp'] - min_global_time).between(start_time, end_time)]
    
    # Format the date and time window for the main plot title.
    p_date = f'{date[5:7]}/{date[8:10]} {date[11:13]}:{date[14:16]}:{date[17:19]}'
    start_s = start_time / 1e7
    end_s = end_time / 1e7
    fig.suptitle(f'{p_date} \n Event Time Window: {start_s:.4f} s - {end_s:.4f} s', fontsize=10)

    # --- Initialize Data Arrays & Plot Axes ---
    min_event_time = min(df_cut['timestamp']) if not df_cut.empty else 0
    
    # These will hold the mapped data for the 21x21 anode plane.
    adc_data = np.zeros((21, 21))
    time_data = np.zeros((21, 21))
    masked_data = np.zeros((21, 21)) # For visualizing disabled channels

    # Setup the central ADC vs. Time plot
    ax[2].set_xlabel('Time [0.1 us]')
    ax[2].set_ylabel('ADC Counts (Pedestal Subtracted)')
    ax[2].grid()

    # Setup the two XY heatmaps (ADC and Time)
    for i in range(2):
        ax[i].axis('off')
        ax[i].hlines([0, 7, 14, 21], 0, 21, color='black', lw=1)
        ax[i].vlines([0, 7, 14, 21], 0, 21, color='black', lw=1)

    # Add a secondary x-axis to the ADC vs. Time plot to show drift distance.
    # The function converts from time ticks to cm.
    func = lambda x: (x / drift_time) * d
    inv = lambda x: (x / d) * drift_time
    secax = ax[2].secondary_xaxis('top', functions=(func, inv))
    secax.set_xlabel('Reconstructed Z-position [cm]')
    
    # Setup histograms
    ax[3].grid(alpha=0.5)
    ax[3].set_xlabel('ADC Counts')
    ax[3].set_ylabel('Number of Hits')
    ax[4].grid(alpha=0.5)
    ax[4].set_xlabel('Time [0.1 us]')
    ax[4].set_ylabel('Number of Hits')
    ax[4].hist([t - min_event_time for t in df_cut['timestamp']], bins=20, histtype='step', color=cm.plasma(0.7))

    # --- Main Data Processing and Plotting Loop ---
    # This loop iterates through every physical pixel location, finds the corresponding
    # data, performs pedestal subtraction, and populates the plots.
    i = 0
    channel_masks = channel_mask()
    adc_lst = [] # To store all ADC values for the histogram
    
    # Use the same mapping arrays as before
    chip_array = np.array([[14, 13, 12], [24, 23, 22], [34, 33, 32]])
    channel_array = np.array([[28, 19, 20, 17, 13, 10,  3], [29, 26, 21, 16, 12,  5,  2],
                              [30, 27, 18, 15, 11,  4,  1], [31, 32, 42, 14, 49,  0, 63],
                              [33, 36, 43, 46, 50, 59, 62], [34, 37, 44, 47, 51, 58, 61],
                              [35, 41, 45, 48, 53, 52, 60]])

    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                chip_df = df_cut.loc[df_cut['chip_id'] == chip_id]
                # Determine which color to use for this chip's hits in the scatter plot
                a, b = np.where(chip_array == chip_id)
                color_idx = 2 * a[0] + b[0] # A unique index from 0-8 for each chip

                masked = channel_masks.get(str(chip_id))

                for channel_idx, channel_id_val in enumerate(channel_lst):
                    x = i // 3
                    y = (i * 7) % channel_idx if (i * 7) % 21 + channel_idx < 21 else (i * 7) % 21 + channel_idx - 21


                    channel_df = chip_df.loc[chip_df['channel_id'] == channel_id_val]
                    
                    # --- CRITICAL STEP: Pedestal Subtraction ---
                    adc_ped_subtracted = [val - pedestal[x][y] for val in channel_df['dataword']]
                    time = [t - min_event_time for t in channel_df['timestamp']]
                    
                    # Store whether this channel was masked off
                    if masked:
                        masked_data[x][y] = masked[channel_id_val]
                    
                    if adc_ped_subtracted:
                        # Populate the ADC vs. Time scatter plot
                        ax[2].scatter(time, adc_ped_subtracted, color=cm.plasma(color_idx / 8), s=10)
                        
                        # Add pedestal-subtracted values to list for histogram
                        adc_lst.extend(adc_ped_subtracted)

                        # For the heatmaps, use the mean value if there are multiple hits on one pixel
                        adc_data[x][y] = np.mean(adc_ped_subtracted)
                        time_data[x][y] = np.mean(time)
            i += 1

    # Now that all data is processed, create the final plots
    ax[3].hist(adc_lst, bins=20, histtype='step', color=cm.plasma(0.3))
    
    # Create a boolean mask to hide pixels with no hits in the heatmaps
    data_mask = (adc_data == 0)

    # Get min values for color scales, ignoring zeros.
    min_adc = np.min(adc_data[~data_mask]) if not data_mask.all() else 0
    min_time = np.min(time_data[~data_mask]) if not data_mask.all() else 0

    # Draw the heatmaps using seaborn
    # First, draw a background showing the masked-off channels
    sns.heatmap(masked_data, vmin=0, vmax=3, cmap='Greys', cbar=False, linewidths=0.1, ax=ax[0])
    sns.heatmap(masked_data, vmin=0, vmax=3, cmap='Greys', cbar=False, linewidths=0.1, ax=ax[1])

    # Overlay the actual data on top of the masked channel background
    sns.heatmap(adc_data, mask=data_mask, vmin=min_adc, cmap='plasma_r', linewidths=0.1, ax=ax[0], linecolor='darkgray', cbar_kws={'label': 'Mean ADC'})
    sns.heatmap(time_data, mask=data_mask, vmin=min_time, cmap='plasma_r', linewidths=0.1, ax=ax[1], linecolor='darkgray', cbar_kws={'label': 'Mean Time [0.1 us]'})


def main(filename, pedestal, hits=6):
    """
    Main function to drive the analysis. It loads a file, scans for track
    candidates, and generates a PDF of plots for them.
    """
    bins = 10000  # The number of time slices to divide the run into for scanning.
    
    df, date = parse_file(filename)
    
    # It's better to load the pedestal from the text file here.
    # For now, this assumes pedestal is the raw HDF5 file.
    ped = parse_pedestal(pedestal) # Replace with np.loadtxt('pedestal_...txt')
    
    if df.empty:
        return

    min_time = min(df['timestamp'])
    max_time = max(df['timestamp']) - min_time
    bin_size = max_time / bins
    
    # --- Event Finding Algorithm ---
    # This loop slices the data into `bins` number of time windows and checks
    # if the number of hits in that window exceeds a threshold (`hits`).
    candidate_windows = []
    for i in range(bins):
        t_min = bin_size * i
        t_max = bin_size * (i + 1)
        cut_df = df[(df['timestamp'] - min_time).between(t_min, t_max)]
        if len(cut_df) > hits:
            candidate_windows.append([t_min, t_max])
            
    if not candidate_windows:
        return
        
    # To avoid noisy runs with thousands of "tracks", cap the number of plots.
    if len(candidate_windows) > 20:
        print(f"Warning: Found {len(candidate_windows)} candidate tracks. Capping at 20 to save time.")
        candidate_windows = candidate_windows[:20]
        
    # --- PDF Generation ---
    # Create one plot for each candidate window and save them all to one PDF.
    pdf_filename = f'all_tracks_{date}.pdf'
    with PdfPages(pdf_filename) as p:
        print(f"Generating {len(candidate_windows)} track plots for {pdf_filename}...")
        for window in candidate_windows:
            start_time = window[0]
            end_time = window[1]
            # This creates the figure but doesn't show it on screen.
            plot_xy_selected(df, start_time, end_time, ped, date)
            # Save the current figure to the PDF file.
            p.savefig(plt.gcf())
            # Close the figure to free up memory.
            plt.close()

if __name__ == '__main__':
    # This block allows the script to be run from the command line,
    # making it flexible for batch processing.
    parser = argparse.ArgumentParser(description="Find and plot candidate tracks in TinyTPC data.")
    parser.add_argument('filename', type=str, help='Input processed HDF5 file (not raw)')
    parser.add_argument('pedestal', type=str, help='Input pedestal HDF5 file (raw)')
    parser.add_argument('--hits', default=10, type=int, help='Minimum number of hits in a time window to define a track candidate.')
    args = parser.parse_args()
    main(**vars(args))