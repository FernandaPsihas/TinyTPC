import os
import xy_tracks
import convert_rawhdf5_to_hdf5
import data_plots
from tqdm import tqdm
import re
import h5py
import numpy as np
import pandas as pd
#converts all data files in a directory and finds events with >10 hits

pedestal = 'put the pedestal here'

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
                              [35, 41, 45, 48, 53, 52, 60]])
    
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

print(len(conv_files), 'files to look at!')
conv_files = sorted(conv_files)
# print(conv_files)

regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}') 
date = regex.search(pedestal).group()
output_filename = f'pedestal_{date}.txt'

if output_filename not in files:
    conv_files(pedestal)

for filename, t in zip(conv_files, tqdm(range(len(conv_files)))):
    # data_plots.main(filename, output_filename)
    xy_tracks.main(filename, output_filename)
    pass