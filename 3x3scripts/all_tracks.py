import os
import xy_tracks
import convert_rawhdf5_to_hdf5
import data_plots
from tqdm import tqdm
#converts all data files in a directory and finds events with >10 hits

files = os.listdir()

conv_files = []
for filename in files:
    if 'tile-id-tile' in filename:
        if 'pedestal' in filename:
            continue
        elif '-raw' in filename:
            output_filename = filename[:12]+'-'+filename[17:]
            if output_filename in files:
                conv_files.append(output_filename)
                #print(output_filename, 'already exists!')
            elif 'conv' in filename:
                conv_files.append(filename)
            else:
                convert_rawhdf5_to_hdf5.main(filename, output_filename, 10240)
                #print(output_filename, 'converted!!')
                conv_files.append(output_filename)

print(len(conv_files), 'files to look at!')
conv_files = sorted(conv_files)
# print(conv_files)

for filename, t in zip(conv_files, tqdm(range(len(conv_files)))):
    data_plots.main(filename)
    xy_tracks.main(filename)
    pass
