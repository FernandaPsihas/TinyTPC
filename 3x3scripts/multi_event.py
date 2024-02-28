import matplotlib.pyplot as plt
import pandas as pd
import h5py
import numpy as np
from matplotlib.colors import Normalize
import argparse
import seaborn as sns
from matplotlib.colors import LogNorm, Normalize
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages
import os
import re

V = 4 # in kV  ||| Rough Measurements for tinyTPC
d = 14 # in cm
T = 90 # in K
T_0 = 89

E = V/d

a_0 = 551.6
a_1 = 7158.3
a_2 = 4440.43
a_3 = 4.29
a_4 = 43.63
a_5 = 0.2053

mu = ((a_0 + a_1*E + a_2*E**(3/2) + a_3*E**(5/2))/(1+(a_1/a_0)*E + a_4*E**2 + a_5*E**3))*(T/T_0)**(-3/2) #cm^2/V/s
v = mu*E*1000 #cm/s
drift_time = (d/v)*1e7 #0.1 us


def parse_file(filename):
    """
    Reads the .h5 file from the pedestal run and turns it into a readable dataframe
    Parameters
    ----------
    filename : str
        Name of the pedestal file.

    Returns
    -------
    df : DataFrame
        Dataframe containing all data
    date: str
        String containing the date

    """
    f = h5py.File(filename,'r')

    df = pd.DataFrame(f['packets'][:])
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]
    
    regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}') 
    date = regex.search(filename).group()   
    return df, date


def parse_json(json_filename):
    f = open(json_filename)

    off = []
    for line in f: 
        if 'channel_mask' in line:
            for i in line:
                if i == '1' or i == '0':
                    off.append(int(i))
    return off


def ADC_to_charge(ADC):
    """
    Converts ADC to charge

    Parameters
    ----------
    ADC : int
        ADC

    Returns
    -------
    pkt_charge : float
        Charge

    """
    VDDA = 1800
    vref_dac = 185
    vcm_dac = 41
    csa_gain = 0
    
    vref = VDDA*(vref_dac/265)
    vcm = VDDA*(vcm_dac/256)
    gain = 4 - 2*csa_gain
    pkt_charge = ADC*((vref-vcm)/256)/gain
    return pkt_charge


def channel_mask():
    path = os.path.realpath(__file__) 
    dir = os.path.dirname(path) 
    
    j_dir = dir+'/configs'
    
    d = dict()
    os.chdir(j_dir) 
    files = os.listdir()
    for file in files:
        chip_id = int(file[24:26])
        channel_mask = parse_json(file)
        d[chip_id] = channel_mask
    
    os.chdir(dir) 
    return(d)


def read_pedestal():
    #add pedestal .txt file in manually here:
    filename = 'pedestal_02_23_13_20_04.txt'
    x = np.genfromtxt(filename)
    return x


def plot_xy_selected(df, date = ''):
    time_lst = list(df['timestamp'])
    min_time = min(df['timestamp'])

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
    time_data = np.arange(441).reshape((21, 21))
    masked_data = np.arange(441).reshape((21, 21))

    dit = channel_mask()
    ped = read_pedestal()
    i = 0
    adc_lst = []
    for chip_lst in chip_array:    
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                chip = df.loc[df['chip_id'] == chip_id]
                a, b = np.where(chip_array == chip_id)
                c = 2*a[0]+b[0]

                if chip_id in dit.keys():
                    masked = dit[chip_id]
                else:
                    masked = None

                for channel_id in range(len(channel_lst)):
                    x = int(i/3)
                    y = (i*7)%21 + channel_id
                    
                    if len(chip) == 0:
                        masked_data[x][y] = 1

                    channel = chip.loc[chip['channel_id']==channel_lst[channel_id]]
                    
                    adc = list(channel['dataword'])
                    time = list(channel['timestamp'])
                    time = [t - min_time for t in time]

                    if masked != None:
                        masked_data[x][y] = masked[channel_lst[channel_id]]
                    else:
                        masked_data[x][y] = 0

                    if len(adc) == 0:
                        adc_data[x][y] = 0
                        time_data[x][y] = 0
                    else:
                        # ax[2].scatter(time, adc - ped[x][y], color=cm.plasma(c/6))
                        for a in adc:
                            adc_lst.append(a - ped[x][y])
                        adc_data[x][y] = np.mean(adc) - ped[x][y]

                        time_data[x][y] = np.mean(time)
                i += 1
    return adc_data, time_data, masked_data, adc_lst, time_lst
            
fig = plt.figure(figsize=(7, 8))
spec = fig.add_gridspec(3, 2)

ax0 = fig.add_subplot(spec[0, 0])
ax1 = fig.add_subplot(spec[0, 1])
ax2 = fig.add_subplot(spec[1, :])
ax3 = fig.add_subplot(spec[2, 0])
ax4 = fig.add_subplot(spec[2, 1])

fig.set_tight_layout(True)

ax = [ax0, ax1, ax2, ax3, ax4]

files = os.listdir()

conv_files = []
for filename in files:
    if 'tile-id-tile-2024' in filename:
        conv_files.append(filename)

conv_files = sorted(conv_files)
conv_files = conv_files[:10]

adc_lst = []
time_lst = []
mask = 0

adc_hst = []
time_hst = []
for file in range(len(conv_files)):
    bins = 10000
    
    df, date = parse_file(conv_files[file])
    

    min_time = min(df['timestamp'])
    
    time = [t - min_time for t in df['timestamp']]
    
    max_time = max(time)
    bin_size = int(max_time/bins)
    
    for i in range(0, bins):
        t_min = bin_size*i
        t_max = bin_size*(i+1)
        cut_df = df[(df['timestamp']-min_time).between(t_min, t_max)]
        if 6<len(cut_df)<30:
            adc_data, time_data, masked_data, adcs, times = plot_xy_selected(cut_df, date)
            adc_lst.append(adc_data)
            time_lst.append(time_data)
            mask = masked_data
            for a, t in zip(adcs, times):
                ax[2].scatter(t, a, color = cm.summer(0.1))
                adc_hst.append(a)
                time_hst.append(t)
    print(file+1)
            

tot_adc = np.stack(adc_lst, axis = 0)
tot_time = np.stack(time_lst, axis = 0)

mean_adc = tot_adc.mean(axis = 0)
mean_time = tot_time.mean(axis = 0)

for i in range(2):
    ax[i].axis('off')
    ax[i].hlines([0, 7, 14, 21], 0, 21, color = 'black', lw = 1)
    ax[i].vlines([0, 7, 14, 21], 0, 21, color = 'black', lw = 1)

data_mask = mean_adc == 0

min_adc = np.min(mean_adc[np.nonzero(mean_adc)])
min_time = np.min(mean_time[np.nonzero(mean_time)])

ax[2].set_xlabel('Time [0.1 us]')
ax[2].set_ylabel('ADC')
ax[2].grid(alpha = 0.5)

ax[3].grid(alpha = 0.5)
ax[3].set_xlabel('ADC')
ax[3].set_ylabel('# hits')

ax[4].grid(alpha = 0.5)
ax[4].set_xlabel('Time [0.1us]')
ax[4].set_ylabel('# hits')

ax[3].hist(adc_hst, bins = 50,
            histtype=u'step', color=cm.summer(0.3))
ax[4].hist(time_hst, bins = 50,
            histtype=u'step', color=cm.summer(0.3))

sns.heatmap(mask, vmin = 0, vmax = 3, cmap = 'Greys', 
                linewidths = 0.1, ax=ax[0], cbar = False)
sns.heatmap(mask, vmin = 0, vmax = 3, cmap = 'Greys', 
                linewidths = 0.1, ax=ax[1], cbar = False)

sns.heatmap(mean_adc, vmin = min_adc, mask = data_mask, cmap = 'summer', 
                linewidths = 0.1, ax=ax[0], linecolor='darkgray', cbar_kws={'label': 'ADC'})
sns.heatmap(mean_time, vmin = min_time, mask = data_mask, cmap = 'summer', 
                linewidths = 0.1, ax=ax[1], linecolor='darkgray', cbar_kws={'label': 'Time'})

plt.savefig('multi_events.png')
plt.show()

    

# print(time)            
        # p = PdfPages(f'all_tracks_{date}.pdf') 
        # figs = [plt.figure(n) for n in fig_nums] 
     
        # for fig in figs:  
        #     fig.savefig(p, format='pdf')  
        # plt.close('all')  
        # p.close()
    
    # p = PdfPages(f'total_tracks.pdf') 
    # figs = [plt.figure(n) for n in fig_nums] 
 
    # for fig in figs:  
    #     fig.savefig(p, format='pdf')  
    # plt.close('all')  
    # p.close()
   
    # print(f'all_tracks_{date}.pdf', 'FINISHED!!!')


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--filename', type=str, help='''Input hdf5 file''')
#     parser.add_argument('--hits', default=10, type=int, help='''ADC cutoff for potential tracks (default = 10)''')
#     args = parser.parse_args()
#     main(**vars(args))
