# Description:
# This script generates a set of diagnostic plots that summarize the performance
# of the entire TinyTPC anode plane over a complete data run. It produces
# run-wide statistics like mean ADC, standard deviation of ADC, and hit rate
# for each channel, visualizing them as 2D heatmaps. It also creates
# per-chip plots of ADC distributions and ADC vs. time. The output is a
# single PDF containing all summary figures for easy inspection.

import matplotlib.pyplot as plt
import h5py
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import argparse
import re
import os

# NOTE on Redundancy: The following two functions are also present in other scripts.
# In a larger project, it's good practice to move common utility functions
# like these into a single, importable 'utils.py' file to avoid code duplication.

def parse_pedestal(filename):
    """
    DEPRECATED/REDUNDANT: This function recalculates the pedestal map from a raw
    pedestal file. The recommended workflow is to generate the pedestal map once
    using a dedicated script, save it to a .txt file, and have all analysis

    scripts load that .txt file using `np.loadtxt()`. This is much faster.
    """
    with h5py.File(filename, 'r') as f:
        df = pd.DataFrame(f['packets'][:])
    df = df.loc[(df['packet_type'] == 0) & (df['valid_parity'] == 1)]

    channel_array = np.array([[28, 19, 20, 17, 13, 10,  3], [29, 26, 21, 16, 12,  5,  2],
                              [30, 27, 18, 15, 11,  4,  1], [31, 32, 42, 14, 49,  0, 63],
                              [33, 36, 43, 46, 50, 59, 62], [34, 37, 44, 47, 51, 58, 61],
                              [35, 41, 45, 48, 53, 52, 60]])
    chip_array = np.array([[14, 13, 12], [24, 23, 22], [34, 33, 32]])
    adc_data = np.zeros((21, 21))
    i = 0
    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                chip = df.loc[df['chip_id'] == chip_id]
                for channel_idx, channel_id_val in enumerate(channel_lst):
                    x = i // 3
                    y = (i * 7) % 21 + channel_idx
                    channel = chip.loc[chip['channel_id'] == channel_id_val]
                    adc = list(channel['dataword'])
                    adc_data[x][y] = np.mean(adc) if adc else 0
            i += 1
    return adc_data


def parse_file(filename):
    """
    Reads a processed HDF5 data file, filters for valid data packets,
    and returns a pandas DataFrame along with the run's date string.
    """
    with h5py.File(filename, 'r') as f:
        df = pd.DataFrame(f['packets'][:])
    df = df.loc[(df['packet_type'] == 0) & (df['valid_parity'] == 1)]
    regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}') 
    date = regex.search(filename).group()   
    return df, date

# NOTE: The channel_mask functions are commented out. If you need to visualize
# masked channels, these would be re-enabled.

def plot_xy_and_key(df, pedestal, date):
    """
    Creates the main summary plot with four panels:
    1. Mean ADC (pedestal-subtracted) per pixel.
    2. Standard Deviation of ADC per pixel.
    3. Hit Rate (in Hz) per pixel.
    4. A key showing the LArPix channel number for each pixel.
    """
    # --- Figure Setup ---
    fig, ax = plt.subplots(1, 4, figsize=(16, 4.5)) # Increased height for better title spacing
    date_str = f'{date[5:7]}/{date[8:10]} {date[11:13]}:{date[14:16]}:{date[17:]}'
    fig.suptitle(f'Run Summary: {date_str}', fontsize=16)
    
    # --- Axis Formatting ---
    # Annotate the plots with chip IDs to make them easier to read.
    for i in range(3):
        ax[i].axis('off')
        ax[i].hlines([0, 7, 14, 21], 0, 21, color='black', lw=1)
        ax[i].vlines([0, 7, 14, 21], 0, 21, color='black', lw=1)
        annotations = {'14': (3.5, 3.5), '13': (10.5, 3.5), '12': (17.5, 3.5),
                       '24': (3.5, 10.5), '23': (10.5, 10.5), '22': (17.5, 10.5),
                       '34': (3.5, 17.5), '33': (10.5, 17.5), '32': (17.5, 17.5)}
        for chip_id, pos in annotations.items():
            ax[i].annotate(chip_id, xy=pos, ha='center', va='center')
    
    ax[0].set_title('Mean ADC')
    ax[1].set_title('RMS of ADC')
    ax[2].set_title('Hit Rate [Hz]')
    ax[3].set_title('Channel ID Key')
    ax[3].axis('off')
    fig.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust layout to make room for suptitle
    
    # --- Data Calculation ---
    # Calculate total livetime of the run in seconds for rate calculation.
    livetime = (max(df['timestamp']) - min(df['timestamp'])) / 1e7 # Clock is 10 MHz
    
    # Anode plane mapping arrays
    channel_array = np.array([[28, 19, 20, 17, 13, 10,  3], [29, 26, 21, 16, 12,  5,  2],
                              [30, 27, 18, 15, 11,  4,  1], [31, 32, 42, 14, 49,  0, 63],
                              [33, 36, 43, 46, 50, 59, 62], [34, 37, 44, 47, 51, 58, 61],
                              [35, 41, 45, 48, 53, 52, 60]])
    chip_array = np.array([[14, 13, 12], [24, 23, 22], [34, 33, 32]])

    # Initialize arrays to hold the data for each heatmap
    mean_data = np.zeros((21, 21))
    std_data = np.zeros((21, 21))
    rate_data = np.zeros((21, 21))
    off_chips_mask = np.ones((21, 21)) # Mask for channels that have no data

    # --- Main Data Mapping Loop ---
    i = 0
    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                chip = df.loc[df['chip_id'] == chip_id]
                for channel_idx, channel_id_val in enumerate(channel_lst):
                    x = i // 3
                    y = (i * 7) % 21 + channel_idx
                    
                    if chip.empty:
                        # Mark this pixel as belonging to an offline chip
                        off_chips_mask[x, y] = 1 

                    channel = chip.loc[chip['channel_id'] == channel_id_val]
                    # --- Pedestal Subtraction ---
                    adc = [val - pedestal[x, y] for val in channel['dataword']]
                    
                    if not adc:
                        # If a channel has no hits, its stats are all zero.
                        mean_data[x, y] = 0
                        std_data[x, y] = 0
                        rate_data[x, y] = 0
                    else:
                        off_chips_mask[x, y] = 0 # This channel is on
                        mean_data[x, y] = np.mean(adc)
                        std_data[x, y] = np.std(adc)
                        rate_data[x, y] = len(adc) / livetime
            i += 1

    # --- Plotting Heatmaps ---
    # Use Seaborn for nice-looking heatmaps.
    sns.heatmap(mean_data, vmin=0, vmax=100, cmap='YlGnBu', linewidths=0.1, ax=ax[0], linecolor='darkgray', cbar_kws={'label': 'Mean ADC'})
    sns.heatmap(std_data, vmin=0, vmax=25, cmap='YlGnBu', linewidths=0.1, ax=ax[1], linecolor='darkgray', cbar_kws={'label': 'RMS of ADC'})
    sns.heatmap(rate_data, vmin=0, cmap='YlGnBu', vmax=max(0.5, np.max(rate_data)), linewidths=0.1, ax=ax[2], linecolor='darkgray', cbar_kws={'label': 'Rate [Hz]'})
    sns.heatmap(channel_array, annot=True, fmt="d", cmap='viridis', linewidths=0.1, ax=ax[3], linecolor='darkgray', cbar_kws={'label': 'Channel #'})
    
    # Overlay a gray mask on top of any channels that were completely off.
    # The mask is boolean, True means "hide this cell".
    for i in range(3):
        sns.heatmap(off_chips_mask, mask=(off_chips_mask == 0), cmap='Greys', cbar=False, ax=ax[i], vmin=0, vmax=2)


def plot_adc_trigger(df, pedestal, date=''):
    """
    Creates a 3x3 grid of histograms, one for each chip. Each histogram shows
    the distribution of pedestal-subtracted ADC values for all its channels.
    """
    fig, ax = plt.subplots(3, 3, figsize=(16, 8), sharex=True, sharey=True)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.suptitle("Pedestal-Subtracted ADC Distributions per Chip", fontsize=16)

    chip_array = np.array([[14, 13, 12], [24, 23, 22], [34, 33, 32]])
    channel_array = np.array([[28, 19, 20, 17, 13, 10,  3], [29, 26, 21, 16, 12,  5,  2],
                              [30, 27, 18, 15, 11,  4,  1], [31, 32, 42, 14, 49,  0, 63],
                              [33, 36, 43, 46, 50, 59, 62], [34, 37, 44, 47, 51, 58, 61],
                              [35, 41, 45, 48, 53, 52, 60]])
    i = 0
    for k in range(3):
        for l in range(3):
            chip_id = chip_array[k,l]
            ax[k,l].grid(alpha=0.5)
            ax[k,l].set_xlabel('ADC Counts')
            ax[k,l].set_ylabel('Hit Count')
            ax[k,l].set_title(f'Chip ID: {chip_id}')
            ax[k,l].set_yscale('log') # Log scale is essential for seeing low-statistic features.

            chip_df = df.loc[df['chip_id'] == chip_id]
            
            # This logic is a bit complex. It iterates through the physical layout
            # to ensure the correct pedestal is applied.
            for channel_lst in channel_array:
                for geo_chip_id in chip_array[i//21]: # This nested structure is confusing. A direct chip loop is better.
                    if geo_chip_id == chip_id:
                        for channel_idx, channel_id_val in enumerate(channel_lst):
                            x = (i // 3)
                            y = (i % 3) * 7 + channel_idx
                            pedestal_val = pedestal[x, y]
                            channel = chip_df.loc[chip_df['channel_id'] == channel_id_val]
                            adc = [val - pedestal_val for val in channel['dataword']]
                            
                            # Color each channel's histogram differently to see their individual contributions.
                            weight = channel_id_val / 64.0
                            ax[k, l].hist(adc, bins=np.linspace(0, 100, 101), log=True, histtype='step',
                                          alpha=0.8, color=cm.viridis(weight), lw=0.5)
                i += 1 # This counter logic is complex and tied to the outer loops.

def plot_adc_time(df, pedestal, date=''):
    """
    Creates a 3x3 grid of scatter plots, one for each chip, showing
    pedestal-subtracted ADC vs. Time for every hit.
    """
    fig, ax = plt.subplots(3, 3, figsize=(16, 8), sharex=True, sharey=True)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.suptitle("ADC vs. Time per Chip", fontsize=16)

    min_time = min(df['timestamp']) if not df.empty else 0
    chip_array = np.array([[14, 13, 12], [24, 23, 22], [34, 33, 32]])
    channel_array = np.array([[28, 19, 20, 17, 13, 10,  3], [29, 26, 21, 16, 12,  5,  2],
                              [30, 27, 18, 15, 11,  4,  1], [31, 32, 42, 14, 49,  0, 63],
                              [33, 36, 43, 46, 50, 59, 62], [34, 37, 44, 47, 51, 58, 61],
                              [35, 41, 45, 48, 53, 52, 60]])
    i = 0
    for k in range(3):
        for l in range(3):
            chip_id = chip_array[k,l]
            ax[k,l].grid(alpha=0.5)
            ax[k,l].set_xlabel('Time [0.1 us]')
            ax[k,l].set_ylabel('ADC Counts')
            ax[k,l].set_title(f'Chip ID: {chip_id}')

            chip_df = df.loc[df['chip_id'] == chip_id]
            if chip_df.empty: continue

            # Similar to above, this loop structure is complex. A more direct approach is safer.
            for channel_lst in channel_array:
                for geo_chip_id in chip_array[i//21]:
                    if geo_chip_id == chip_id:
                        for channel_idx, channel_id_val in enumerate(channel_lst):
                            x = i // 3
                            y = (i % 3) * 7 + channel_idx
                            pedestal_val = pedestal[x, y]
                            channel_df = chip_df.loc[chip_df['channel_id'] == channel_id_val]

                            time = [t - min_time for t in channel_df['timestamp']]
                            adc = [val - pedestal_val for val in channel_df['dataword']]
                            
                            weight = channel_id_val / 64.0
                            ax[k, l].scatter(time, adc, s=2, color=cm.viridis(weight), alpha=0.9)
                i += 1


def main(filename, pedestal, output_dir=None):
    """
    Main function to drive the script. It loads data, calls the plotting
    functions, and saves all figures to a single PDF.
    """
    if output_dir is None:
        output_dir = os.path.dirname(os.path.realpath(__file__))

    print(f"Loading pedestal file: {pedestal}")
    # This is where you would ideally use: ped = np.loadtxt(pedestal_text_file)
    ped = parse_pedestal(pedestal)
    
    print(f"Loading data file: {filename}")
    df, date = parse_file(filename)
    
    if df.empty:
        print(f"File {filename} is empty or contains no valid data packets. Skipping.")
        return # Exit if there's no data to plot.
    
    # --- PDF Generation ---
    # This process will create three figures in memory, then save them all to one PDF.
    output_filename = os.path.join(output_dir, f'summary_plots_{date}.pdf')
    with PdfPages(output_filename) as p:
        print(f"Creating summary plots and saving to {output_filename}...")
        
        # Call each plotting function. A figure is created for each one.
        plot_xy_and_key(df, ped, date)
        p.savefig(plt.gcf()) # Save the current figure to the PDF
        
        plot_adc_trigger(df, ped)
        p.savefig(plt.gcf())
        
        plot_adc_time(df, ped)
        p.savefig(plt.gcf())
        
        # Close all figures to free up memory before the next run.
        plt.close('all')

    print(f'Finished generating summary plots for {date}.')


if __name__ == '__main__':
    # This allows the script to be run from the command line with arguments.
    parser = argparse.ArgumentParser(description="Generate summary diagnostic plots for a TinyTPC data run.")
    parser.add_argument('filename', help='Input data hdf5 file.')
    parser.add_argument('pedestal', help='Pedestal hdf5 file.')
    parser.add_argument('-o', '--output_dir', default=os.getcwd(), help='Directory to save the output PDF file.')
    args = parser.parse_args()
    main(args.filename, args.pedestal, args.output_dir)