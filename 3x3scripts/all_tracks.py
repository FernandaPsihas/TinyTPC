import os
import xy_tracks
import convert_rawhdf5_to_hdf5
import data_plots
from tqdm import tqdm
import re
import h5py
import numpy as np
import pandas as pd
import gc
import glob
import argparse
import pedestal_plots

#converts all data files in a directory and finds events with >10 hits

# will by default run in current directory, add desired directory in terminal when running it to have it run somewhere else
# ex: python3.10 all_tracks.py /home/hmccright/Neutrinos/old_script_testing/latest/2024_07_19_08-33_CT
parser = argparse.ArgumentParser(description="Process HDF5 files in a directory.")
parser.add_argument("directory", nargs="?", default=".", help="Path to the target directory (default: current directory)")
args = parser.parse_args()
directory = os.path.abspath(args.directory)
os.chdir(directory)

# Look for all pedestal files matching the pattern
pedestal_pattern = "tile-id-3x3-pedestal_*.h5"
all_ped_names = glob.glob(pedestal_pattern)

# Filter out "FAILED" files
valid_ped_names = [name for name in all_ped_names if "FAILED" not in name]

if valid_ped_names:
    pedestal = valid_ped_names[0]
    print("Using pedestal file:", pedestal)

    # Extract the date from the filename to construct the expected PDF filename
    match = re.search(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}', pedestal)
    if match:
        date = match.group()
        pdf_filename = f'pedestal_{date}.pdf'

        if os.path.exists(pdf_filename):
            print(f"Plot already exists: {pdf_filename} — skipping pedestal plotting.")
        else:
            print("Plot not found — generating now...")
            pedestal_plots.main(pedestal)
    else:
        print("Could not extract date from pedestal filename — skipping plotting.")

else:
    if all_ped_names:
        print("All pedestal files found are marked as FAILED:")
        for f in all_ped_names:
            print("  ", f)
    else:
        print("No pedestal files found at all.")




def conv_pedestal(filename):

    start_time = 0
    end_time = 60

    f = h5py.File(filename,'r')


    df = pd.DataFrame(f['packets'][:])
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]

    channel_array = np.array([[28, 19, 20, 17, 13, 10,  3],
                              [29, 26, 21, 16, 12,  5,  2],
                              [30, 27, 18, 15, 11,  4,  1],
                              [31, 32, 42, 14, 49,  0, 63],
                              [33, 36, 43, 46, 50, 59, 62],
                              [34, 37, 44, 47, 51, 58, 61],
                              [35, 41, 45, 48, 53, 52, 60]]) #this

    chip_array = np.array([[14, 13, 12],
                           [24, 23, 22],
                           [34, 33, 32]])

    adc_data = np.arange(441).reshape((21, 21))

    i = 0
    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                chip = df.loc[df['chip_id'] == chip_id]
                for channel_id in range(len(channel_lst)):
                    x = int(i/3)
                    y = (i*7)%21 + channel_id

                    channel = chip.loc[chip['channel_id']==channel_lst[channel_id]]

                    adc = list(channel['dataword'])

                    if len(adc) == 0:
                        adc_data[x][y] = 0
                    else:
                        adc_data[x][y] = np.mean(adc)
                i += 1

    regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}')
    date = regex.search(filename).group()
    np.savetxt(f'pedestal_{date}.txt', adc_data)

files = os.listdir()

conv_files = []
for filename in files:
    if 'tile-id-' in filename:
        if 'pedestal' in filename:
            continue
        elif '-raw' in filename:
            regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}')
            date = regex.search(filename).group()
            output_filename = f'tile-id-3x3_{date}.h5'
            if output_filename in files:
                conv_files.append(output_filename)
                #print(output_filename, 'already exists!')
            # elif 'conv' in filename:
            #     conv_files.append(filename)
            else:
                convert_rawhdf5_to_hdf5.main(filename, output_filename, 10240)
                #print(output_filename, 'converted!!')
                conv_files.append(output_filename)

print('converted files!')

print(len(conv_files), 'files to look at!')
conv_files = sorted(conv_files)
# print(conv_files)

regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}')
#date = regex.search(pedestal).group()
#output_filename = f'pedestal_{date}.txt'

if output_filename not in files:
    conv_pedestal(pedestal)

for filename, t in zip(conv_files, tqdm(range(len(conv_files)))):
    data_plots.main(filename, pedestal)
    print("weezer blue plots have been made")
    xy_tracks.main(filename, pedestal)
    print("xy did it's thing")
    gc.collect()

    pass
