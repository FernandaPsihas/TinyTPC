import matplotlib.pyplot as plt
import h5py
import numpy as np
import matplotlib.cm as cm
import pandas as pd
# from matplotlib.lines import Line2D
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import argparse
import re
import os

def parse_pedestal(filename):
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
    
    # regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}') 
    # date = regex.search(filename).group()
    # np.savetxt(f'pedestal_{date}.txt', adc_data)
    return(adc_data)


def parse_file(filename):
    """
    Reads the .h5 file from the data run and turns it into a readable dataframe
    Parameters
    ----------
    filename : str
        Name of the data file.

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


# def parse_json(json_filename):
#     f = open(json_filename)

#     off = []
#     for line in f: 
#         if 'channel_mask' in line:
#             for i in line:
#                 if i == '1' or i == '0':
#                     off.append(int(i))
#     return off


# def channel_mask():
#     path = os.path.realpath(__file__) 
#     dir = os.path.dirname(path) 
#     j_dir = dir + '/configs'
    
#     d = dict()
#     os.chdir(j_dir) 
#     files = os.listdir()
#     for file in files:
#         regex = re.compile(r'\d{1}-\d{1}-\d{2}')
#         stri = regex.search(file).group()

#         chip_id = stri[4:]
#         channel_mask = parse_json(file)
#         d[chip_id] = channel_mask
    
#     os.chdir(dir) 
#     return d

# def read_pedestal(pedestal):
#     x = np.genfromtxt(pedestal)
#     return x

def plot_xy_and_key(df, pedestal, date):
    """
    Creates a 2d histogram plot the mean ADC, std ADC, and rate for each channel and a key showing the channel colors for the trigger/time plots.

    Parameters
    ----------
    df : dataframe
        Dataframe produced by parse_file.
    date : str
        Date produced by parse_file.

    Returns
    -------
    None.

    """
    fig, ax = plt.subplots(1, 4, figsize=(16,3.5))
    date_str = f'{date[5:7]}/{date[8:10]} {date[11:13]}:{date[14:16]}:{date[17:]}'
    plt.suptitle(f'Data {date_str}')
    
    for i in range(3):
        ax[i].axis('off')
        ax[i].hlines([0, 7, 14, 21], 0, 21, color = 'black', lw = 1)
        ax[i].vlines([0, 7, 14, 21], 0, 21, color = 'black', lw = 1)
        
        ax[i].annotate('14', xy = [3.5, 3.5], ha='center', va='center')
        ax[i].annotate('13', xy = [10.5, 3.5], ha='center', va='center')
        ax[i].annotate('12', xy = [17.5, 3.5], ha='center', va='center')
        
        ax[i].annotate('24', xy = [3.5, 10.5], ha='center', va='center')
        ax[i].annotate('23', xy = [10.5, 10.5], ha='center', va='center')
        ax[i].annotate('22', xy = [17.5, 10.5], ha='center', va='center')
        
        ax[i].annotate('34', xy = [3.5, 17.5], ha='center', va='center')
        ax[i].annotate('33', xy = [10.5, 17.5], ha='center', va='center')
        ax[i].annotate('32', xy = [17.5, 17.5], ha='center', va='center')
    
    ax[0].set_title('Mean ADC')
    ax[1].set_title('STD ADC')
    ax[2].set_title('Rate')
    ax[3].set_title('Channel Key')
    ax[3].axis('off')
    fig.set_tight_layout(True)
    
    livetime = (max(df['timestamp'])-min(df['timestamp']))/1e7
    
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

    mean_data = np.zeros(441).reshape((21, 21))
    std_data = np.zeros(441).reshape((21, 21))
    rate_data = np.zeros(441).reshape((21, 21))
    off_chips = np.zeros(441).reshape((21, 21))
    masked_data = np.arange(441).reshape((21, 21))

    # dit = channel_mask()
    i = 0
    # ped = read_pedestal(pedestal)
    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                chip = df.loc[df['chip_id'] == chip_id]
                # if chip_id in dit.keys():
                #     masked = dit[chip_id]
                # else:
                #     masked = None

                for channel_id in range(len(channel_lst)):
                    x = int(i/3)
                    y = (i*7)%21 + channel_id
                    if len(chip) == 0:
                        off_chips[x][y] = 1

                    channel = chip.loc[chip['channel_id']==channel_lst[channel_id]]
                    
                    adc = [a - pedestal[x][y] for a in channel['dataword']]
                    
                    # if masked != None:
                    #     masked_data[x][y] = masked[channel_lst[channel_id]]
                    # else:
                    #     masked_data[x][y] = 0

                    if len(adc) == 0:
                        mean_data[x][y] = 0
                        std_data[x][y] = 0
                        rate_data[x][y] = 0
                    else:
                        mean_data[x][y] = np.mean(adc)
                        std_data[x][y] = np.std(adc)
                        rate_data[x][y] = len(adc)/livetime
                i += 1


    sns.heatmap(mean_data, vmin = 0, cmap = 'YlGnBu', vmax = 100,
                    linewidths = 0.1, ax=ax[0], linecolor='darkgray', cbar_kws ={'label': 'Mean ADC'})
    sns.heatmap(std_data, vmin = 0,  cmap = 'YlGnBu', vmax = 25,  
                    linewidths = 0.1, ax=ax[1], linecolor='darkgray', cbar_kws={'label': 'RMS ADC'})
    sns.heatmap(rate_data, vmin = 0, cmap = 'YlGnBu', vmax = 0.5,
                    linewidths = 0.1, ax=ax[2], linecolor='darkgray', cbar_kws={'label': 'Rate'})
    sns.heatmap(channel_array, vmin = 0, cmap = 'viridis', 
                    linewidths = 0.1, ax=ax[3], linecolor='darkgray', cbar_kws={'label': 'Channel #'})    
    
    # data_mask = masked_data == 0
    # sns.heatmap(masked_data, mask = data_mask, vmin = 0, vmax = 3, cmap = 'Greys', cbar = False, 
    #                 linewidths = 0.1, ax=ax[0], linecolor='darkgray')
    # sns.heatmap(masked_data, mask = data_mask, vmin = 0, vmax = 3, cmap = 'Greys', cbar = False,
    #                 linewidths = 0.1, ax=ax[1], linecolor='darkgray')
    # sns.heatmap(masked_data, mask = data_mask, vmin = 0, vmax = 3, cmap = 'Greys', cbar = False, 
    #                 linewidths = 0.1, ax=ax[2], linecolor='darkgray')

    data_mask = off_chips == 0
    for i in range(3):
        sns.heatmap(off_chips, mask = data_mask, vmin = 0, vmax = 3, cmap = 'Greys', cbar = False,
                        ax=ax[i])
    
    
def plot_adc_trigger(df, pedestal, date = ''):
    """
    Creates a 3x3 histogram plot of the ADC of every channel from each chip.

    Parameters
    ----------
    filename : str
        Name of the pedestal file.

    Returns
    -------
    None.

    """

    fig, ax = plt.subplots(3,3, figsize=(16, 8), sharex = True, sharey = True)
    fig.set_tight_layout(True)

    i = 0
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
    
    # ped = read_pedestal(pedestal)
    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                k, l = np.where(chip_array == chip_id)
                k = int(k[0])
                l = int(l[0])
            
                ax[k][l].grid(alpha = 0.5)
                ax[k][l].set_xlabel('ADC')
                ax[k][l].set_ylabel('trigger count')
                ax[k][l].set_title(f'chip {chip_id}')

                chip = df.loc[df['chip_id'] == chip_id]
                for channel_id in range(len(channel_lst)):
                    x = int(i/3)
                    y = (i*7)%21 + channel_id

                    pedestal_val = pedestal[x][y]
                    channel = chip.loc[chip['channel_id']==channel_lst[channel_id]]

                    adc = [dw - pedestal_val for dw in channel['dataword']]

                    weight = (channel_lst[channel_id])/64

                    ax[k][l].hist(adc, bins = np.linspace(0, 100, 101), log=True, histtype=u'step',
                               alpha = 0.8, color=cm.viridis(weight), lw = 0.5)
                i += 1
    # plt.savefig(f'adc_trigger_{date}.png')
        
        
def plot_adc_time(df, pedestal, date = ''):
    """
    Creates a plot of the ADC vs. the time for every channel on each chip

    Parameters
    ----------
    filename : str
        Name of the pedestal file.

    Returns
    -------
    None.

    """
    cids = [12, 22, 32, 13, 23, 33, 14, 24, 34]
    
    nonrouted_v2a_channels=[6,7,8,9,22,23,24,25,38,39,40,54,55,56,57]
    routed_v2a_channels=[i for i in range(64) if i not in nonrouted_v2a_channels]

    fig, ax = plt.subplots(3, 3, figsize=(16, 8), sharex = True, sharey=True)
    fig.set_tight_layout(True)
    # markers = ['.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
    
    times = []
    for chip_id in cids:
        chip = df.loc[df['chip_id']==chip_id] 
        if len(chip) == 0:
            continue
        else:
            chip_min_time = list(chip['timestamp'])[0]
            times.append(chip_min_time)

    min_time = min(times)
    i = 0
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
    
    # ped = read_pedestal(pedestal)
    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                k, l = np.where(chip_array == chip_id)
                k = int(k[0])
                l = int(l[0])
            
                ax[k][l].grid(alpha = 0.5)
                ax[k][l].set_xlabel('ADC')
                ax[k][l].set_ylabel('trigger count')
                ax[k][l].set_title(f'chip {chip_id}')

                chip = df.loc[df['chip_id'] == chip_id]
                for channel_id in range(len(channel_lst)):
                    x = int(i/3)
                    y = (i*7)%21 + channel_id

                    pedestal_val = pedestal[x][y]
                    channel = chip.loc[chip['channel_id']==channel_lst[channel_id]]

                    time = [t - min_time for t in channel['timestamp']]
                    adc = [dw - pedestal_val for dw in channel['dataword']]

                    weight = (channel_lst[channel_id])/64
                    ax[k][l].scatter(time, adc, s = 2, color=cm.viridis(weight), 
                               alpha = 0.9)
                i += 1
    # plt.savefig(f'adc_time_{date}.png')
    

def main(filename, pedestal, output_dir = str(os.path.dirname(os.path.realpath(__file__)))):
    ped = parse_pedestal(pedestal)
    df, date = parse_file(filename)
    if len(df) == 0:
    	print("weezer")
        #return
    else: 
        fig_nums = []
        plot_xy_and_key(df, ped, date)
        fig_nums.append(plt.gcf().number)
        plot_adc_trigger(df, ped)
        fig_nums.append(plt.gcf().number)
        plot_adc_time(df, ped)
        fig_nums.append(plt.gcf().number)
        
        print("dbfalkfhk")
    
        output_filename = output_dir + f'/data_{date}.pdf'
        p = PdfPages(output_filename) 
        figs = [plt.figure(n) for n in fig_nums] 
 
        for fig in figs:  
            fig.savefig(p, format='pdf')  
        plt.close('all')  
        p.close()
    #print(output_filename, 'Finished!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', '-i', type=str, help='''Input data hdf5 file''')
    parser.add_argument('--pedestal', '-p', type=str, help='''Pedestal hdf5 file''')
    parser.add_argument('--output_dir', '-o', default= str(os.path.dirname(os.path.realpath(__file__))), type=str, help='''Output data hdf5 file''')
    args = parser.parse_args()
    c = main(**vars(args))
