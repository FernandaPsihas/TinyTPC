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

V = 4 # in kV  ||| Rough Measurements for tinyTPC
d = 15 # in cm
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
    return d


def plot_xy_selected(df, start_time, end_time, date = ''):
    
    fig = plt.figure(figsize=(9, 11))
    spec = fig.add_gridspec(3, 2)
    
    ax0 = fig.add_subplot(spec[0, 0])
    ax1 = fig.add_subplot(spec[0, 1])
    ax2 = fig.add_subplot(spec[1, :])
    ax3 = fig.add_subplot(spec[2, 0])
    ax4 = fig.add_subplot(spec[2, 1])
    
    fig.set_tight_layout(True)
    
    ax = [ax0, ax1, ax2, ax3, ax4]

    chip12 = df.loc[df['chip_id'] == 12]
    min_time = min(chip12['timestamp'])
    
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

    df_cut = df[(df['timestamp']-min_time).between(start_time*1e7, (end_time)*1e7)]
    
    p_date = f'{date[5:7]}/{date[8:10]} {date[11:13]}:{date[14:16]}:{date[17:19]}'

    fig.suptitle(f'{p_date} \n {(min(df_cut["timestamp"])-min_time)*1e-7} s - {(max(df_cut["timestamp"])-min_time)*1e-7} s', 
                 fontsize=10)

    min_time = min(df_cut['timestamp'])
    ax[2].set_xlim(min(df_cut['timestamp'])-min_time, max(df_cut['timestamp'])-min_time)
    ax[2].set_xlabel('Time [0.1 us]')
    ax[2].set_ylabel('ADC')
    ax[2].grid()

    for i in range(2):
        ax[i].axis('off')
        ax[i].hlines([0, 7, 14, 21], 0, 21, color = 'black', lw = 1)
        ax[i].vlines([0, 7, 14, 21], 0, 21, color = 'black', lw = 1)
        
        # ax[i].annotate('12', xy = [3.5, 3.5], ha='center', va='center')
        # ax[i].annotate('13', xy = [10.5, 3.5], ha='center', va='center')
        # ax[i].annotate('14', xy = [17.5, 3.5], ha='center', va='center')
        
        # ax[i].annotate('22', xy = [3.5, 10.5], ha='center', va='center')
        # ax[i].annotate('23', xy = [10.5, 10.5], ha='center', va='center')
        # ax[i].annotate('24', xy = [17.5, 10.5], ha='center', va='center')
        
        # ax[i].annotate('32', xy = [3.5, 17.5], ha='center', va='center')
        # ax[i].annotate('33', xy = [10.5, 17.5], ha='center', va='center')
        # ax[i].annotate('34', xy = [17.5, 17.5], ha='center', va='center')

    func = lambda x: (x)/drift_time
    inv = lambda x: (x)*drift_time

    secax = ax[2].secondary_xaxis('top', functions=(func, inv))
    secax.set_xlabel('Drift Time')
    
    ax[3].grid(alpha = 0.5)
    ax[3].set_xlabel('ADC')
    ax[3].set_ylabel('# hits')
    ax[3].hist(df_cut['dataword'], bins = 20, 
               histtype=u'step', color=cm.plasma(0.3))
    
    ax[4].grid(alpha = 0.5)
    ax[4].set_xlabel('Time [0.1us]')
    ax[4].set_ylabel('# hits')
    ax[4].hist([t - min_time for t in df_cut['timestamp']], bins = 20,
               histtype=u'step', color=cm.plasma(0.7))

    i = 0
    dit = channel_mask()
    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                chip = df_cut.loc[df_cut['chip_id'] == chip_id]
                a, b = np.where(chip_array == chip_id)
                c = 2*a[0]+b[0]
                
                if chip_id in dit.keys():
                    masked = dit[chip_id]
                else:
                    masked = None
                    
                for channel_id in range(len(channel_lst)):
                    x = int(i/3)
                    y = (i*7)%21 + channel_id

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
                        ax[2].scatter(time, adc, color=cm.plasma(c/6))
                        adc_data[x][y] = np.mean(adc)

                        time_data[x][y] = np.mean(time)
                i += 1


    data_mask = adc_data == 0

    min_adc = np.min(adc_data[np.nonzero(adc_data)])
    min_time = np.min(time_data[np.nonzero(time_data)])

    sns.heatmap(masked_data, vmin = 0, vmax = 3, cmap = 'Greys', cbar = False, 
                    linewidths = 0.1, ax=ax[0])
    sns.heatmap(masked_data, vmin = 0, vmax = 3, cmap = 'Greys', cbar = False,
                    linewidths = 0.1, ax=ax[1])

    sns.heatmap(adc_data, mask = data_mask, vmin = min_adc, cmap = 'plasma_r', 
                    linewidths = 0.1, ax=ax[0], linecolor='darkgray', cbar_kws={'label': 'ADC'})
    sns.heatmap(time_data, mask = data_mask, vmin = min_time, cmap = 'plasma_r', 
                    linewidths = 0.1, ax=ax[1], linecolor='darkgray', cbar_kws={'label': 'Time'})
    # plt.savefig(f'selected_xy_{date}.png')
        

def main(filename, hits=10):
    bins = 10000
    
    df, date = parse_file(filename)
    
    chip12 = df.loc[df['chip_id'] == 12]
    min_time = min(chip12['timestamp'])
    
    time = [t - min_time for t in df['timestamp']]
    
    max_time = max(time)
    bin_size = int(max_time/bins)
    
    can = []
    for i in range(0, bins):
        t_min = bin_size*i
        t_max = bin_size*(i+1)
        cut_df = df[(df['timestamp']-min_time).between(t_min, t_max)]
        if len(cut_df)>hits:
            can.append([t_min, t_max])
    
    print(len(can), 'potential tracks!')
    
    if len(can) == 0: 
        print('no tracks found!!')
    else:
    
        fig_nums = []
        for i in range(len(can)):
            start_time = can[i][0]/1e7
            end_time = can[i][1]/1e7
            plot_xy_selected(df, start_time, end_time, date)
            fig_nums.append(plt.gcf().number)
            print(i+1, 'done!')
            
        p = PdfPages(f'all_tracks_{date}.pdf') 
        figs = [plt.figure(n) for n in fig_nums] 
     
        for fig in figs:  
            fig.savefig(p, format='pdf')  
        plt.close('all')  
        p.close()
    
    print('FINISHED!!!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, help='''Input hdf5 file''')
    parser.add_argument('--hits', default=10, type=int, help='''ADC cutoff for potential tracks (default = 10)''')
    args = parser.parse_args()
    main(**vars(args))
