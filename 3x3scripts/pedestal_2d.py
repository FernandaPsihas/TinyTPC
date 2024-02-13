import matplotlib.pyplot as plt
import pandas as pd
import h5py
import numpy as np
import argparse
import os

#creates a 2d matrix of pedestal values to be subtracted from raw ADC data - needed for xy_tracks_w_ped.py 

def main(filename):

    start_time = 0
    end_time = 60
    
    f = h5py.File(filename,'r')
    
    
    df = pd.DataFrame(f['packets'][:])
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]

    chip12 = df.loc[df['chip_id'] == 12]
    min_time = min(chip12['timestamp'])

    livetime = np.max(chip12['timestamp'])-min_time

    channel_array = np.array([[28, 19, 20, 17, 13, 10,  3],
                              [29, 26, 21, 16, 12,  5,  2],
                              [30, 27, 18, 15, 11,  4,  1],
                              [31, 32, 42, 14, 49,  0, 63],
                              [33, 36, 43, 46, 50, 59, 62],
                              [34, 37, 44, 47, 51, 58, 61],
                              [35, 41, 45, 48, 53, 52, 60]])
    
    chip_array = np.array([[12, 13, 14],
                           [22, 23, 24],
                           [32, 33, 34]])

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
    date = filename[27:41]
    np.savetxt(f'pedestal_{date}.txt', adc_data)

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, help='''Input hdf5 file''')
    args = parser.parse_args()
    main(**vars(args))
