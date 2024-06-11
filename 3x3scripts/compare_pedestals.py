import matplotlib.pyplot as plt
import yaml
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize
import matplotlib.cm as cm
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


def compare_pedestals(df1, df2, date1 = '', date2 = ''):
    fig, ax = plt.subplots(1, 3, figsize=(16,5))
    date_str1 = f'{date1[5:7]}/{date1[8:10]} {date1[11:13]}:{date1[14:16]}:{date1[17:]}'
    date_str2 = f'{date2[5:7]}/{date2[8:10]} {date2[11:13]}:{date2[14:16]}:{date2[17:]}'
    plt.suptitle(f'Pedestals:\n{date_str1}\n{date_str2}')
    
    for i in range(3):
        ax[i].axis('off')
        ax[i].hlines([0, 7, 14, 21], 0, 21, color = 'black', lw = 1)
        ax[i].vlines([0, 7, 14, 21], 0, 21, color = 'black', lw = 1)
        
        ax[i].annotate('12', xy = [3.5, 3.5], ha='center', va='center')
        ax[i].annotate('13', xy = [10.5, 3.5], ha='center', va='center')
        ax[i].annotate('14', xy = [17.5, 3.5], ha='center', va='center')
        
        ax[i].annotate('22', xy = [3.5, 10.5], ha='center', va='center')
        ax[i].annotate('23', xy = [10.5, 10.5], ha='center', va='center')
        ax[i].annotate('24', xy = [17.5, 10.5], ha='center', va='center')
        
        ax[i].annotate('32', xy = [3.5, 17.5], ha='center', va='center')
        ax[i].annotate('33', xy = [10.5, 17.5], ha='center', va='center')
        ax[i].annotate('34', xy = [17.5, 17.5], ha='center', va='center')
    
    ax[0].set_title('Mean ADC')
    ax[1].set_title('STD ADC')
    ax[2].set_title('Rate')

    fig.set_tight_layout(True)
    
    livetime1 = (max(df1['timestamp'])-min(df1['timestamp']))/1e7
    livetime2 = (max(df2['timestamp'])-min(df2['timestamp']))/1e7
    
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

    mean_data = np.zeros(441).reshape((21, 21))
    std_data = np.zeros(441).reshape((21, 21))
    rate_data = np.zeros(441).reshape((21, 21))
    off_chips = np.zeros(441).reshape((21, 21))

    i = 0
    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                chip1 = df1.loc[df1['chip_id'] == chip_id]
                chip2 = df2.loc[df2['chip_id'] == chip_id]
                for channel_id in range(len(channel_lst)):
                    x = int(i/3)
                    y = (i*7)%21 + channel_id
                    
                    if len(chip1) == 0 and len(chip2) == 0:
                        off_chips[x][y] = 1

                    channel1 = chip1.loc[chip1['channel_id']==channel_lst[channel_id]]
                    channel2 = chip2.loc[chip2['channel_id']==channel_lst[channel_id]]
                    
                    adc1 = list(channel1['dataword'])
                    adc2 = list(channel2['dataword'])
                        
                    if len(adc1) == 0 and len(adc2) == 0:
                        mean_data[x][y] = 0
                        std_data[x][y] = 0
                        rate_data[x][y] = 0
                    else:
                        if np.mean(adc2)==0:
                            mean_data[x][y] = 0
                        else:
                            mean_data[x][y] = np.mean(adc1)/np.mean(adc2)
                        
                        if np.std(adc2) == 0:
                            std_data[x][y] = 0
                        else:
                            std_data[x][y] = np.std(adc1)/np.std(adc2)
                        rate_data[x][y] = (len(adc1)/livetime1)/(len(adc2)/livetime2)
                i += 1

    sns.heatmap(mean_data, vmin = 0, vmax = 2, cmap = 'YlOrRd',
                    linewidths = 0.1, ax=ax[0], linecolor='darkgray', cbar_kws ={'label': 'Mean ADC'})
    sns.heatmap(std_data, vmin = 0, vmax = 2, cmap = 'YlOrRd',  
                    linewidths = 0.1, ax=ax[1], linecolor='darkgray', cbar_kws={'label': 'Std ADC'})
    sns.heatmap(rate_data, vmin = 0, vmax = 2, cmap = 'YlOrRd',
                    linewidths = 0.1, ax=ax[2], linecolor='darkgray', cbar_kws={'label': 'Rate'})
    
    data_mask = off_chips == 0
    for i in range(3):
        sns.heatmap(off_chips, mask = data_mask, vmin = 0, vmax = 3, cmap = 'Greys', cbar = False,
                        ax=ax[i])
        
    output_filename = f'compare_pedestal_{date1}_{date2}.png'
    plt.savefig(output_filename)
    print(output_filename, 'DONE!!')
    


def main(filename1, filename2):
    df1, date1 = parse_file(filename1)
    df2, date2 = parse_file(filename2)
    
    compare_pedestals(df1, df2, date1, date2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename1', type=str, help='''Input pedestal hdf5 file''')
    parser.add_argument('--filename2', type=str, help='''Input other pedestal hdf5 file''')
    args = parser.parse_args()
    c = main(**vars(args))
