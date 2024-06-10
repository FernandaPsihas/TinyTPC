import pandas as pd
import h5py
import numpy as np
import argparse
import os
import re
from tqdm import tqdm

def event_frame(df, start_time, end_time, ind = 0):
    min_time = min(df['timestamp'])

    df = df[(df['timestamp']-min_time).between(start_time, end_time)]

    min_time = min(df['timestamp'])
    
    d = df.loc[:, ('chip_id', 'channel_id', 'timestamp', 'dataword')]
    d['timestamp'] = [t - min_time for t in d['timestamp']]
    
    inds = [ind for i in range(len(d))]
    d['n_event'] = inds
    return d


def all_frame(filename, hits = 6):
    adc = 10
    
    bins = 10000
    
    f = h5py.File(filename,'r')
    
    date = filename[17:]
    date = f'{date[5:7]}_{date[8:10]}_{date[11:13]}-{date[14:16]}-{date[17:19]}'
    
    df = pd.DataFrame(f['packets'][:])
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]
    
    min_time = min(df['timestamp'])
    
    time = [t - min_time for t in df['timestamp']]
    
    max_time = max(time)
    bin_size = int(max_time/bins)
    
    can = []
    for i in range(0, bins):
        t_min = bin_size*i
        t_max = bin_size*(i+1)
        cut_df = df[(df['timestamp']-min_time).between(t_min, t_max)]
        if hits<len(cut_df)<30:
            can.append([t_min, t_max])

    lst = []
    for i in range(len(can)):
        d = event_frame(df, can[i][0], can[i][1], i)
        lst.append(d)

    df_out = pd.concat(lst, ignore_index = True)
    return df_out


def main(filename):
    df_out = all_frame(filename)
    regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}') 
    date = regex.search(filename).group()
    date = f'{date[5:7]}_{date[8:10]}_{date[11:13]}-{date[14:16]}-{date[17:19]}'
    output_filename = f'events_{date}.h5'
    df_out.to_hdf(output_filename, key='df', mode='w')  


files = os.listdir()
file_lst = []
for file in files:
    if 'tile-id-tile-2024' in file:
        file_lst.append(file)

file_lst = sorted(file_lst)

for filename, x in zip(file_lst, tqdm(range(len(file_lst)))):
    regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}')
    date = regex.search(filename).group()
    date = f'{date[5:7]}_{date[8:10]}_{date[11:13]}-{date[14:16]}-{date[17:19]}'
    output_filename = f'events_{date}.h5'
    if output_filename in files:
        continue
        #print(output_filename, 'already done!')
    else:
        main(filename)
        #print(output_filename)
    pass


# if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--filename', type=str, help='''Input hdf5 file''')
    # args = parser.parse_args()
    # main(**vars(args))







