pedestal_plots.py `python3 pedestal_plots.py –-filename "filename"`
creates pink plots

all_tracks.py `python3 all_tracks.py`
will convert all raw data files, create blue data plots, and find >10 hit events for every raw data file in a directory. Does not subtract pedestal values. you can comment out everything after line 30 to convert files in bulk

convert_rawhdf5_to_hdf5.py `python3 convert_rawhdf5_to_hdf5.py –-input_filename "input_filename" --output_filename "output_filename" --block_size "10240"`
converts one raw file

data_plots.py `python3 data_plots.py -–filename "filename"`
makes blue-green plots. needs converted file

xy_tracks.py `python3 xy_tracks.py -–filename "filename"`
finds >10 hit events for one file. if fewer chips are used, max number of hits needs to be changed manually. subtracts pedestal values, needs pedestal .txt file created by pedestal_2d.py, which can be put in manually on line 90

pedestal_2d.py `python3 pedestal_2d.py -–filename "filename"`
turns pedestal into 2d matrix

