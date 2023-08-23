import matplotlib.pyplot as plt
import h5py
import yaml
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import pandas as pd
from matplotlib.lines import Line2D

def find_channel_id(u): 
    return u % 64


def find_chip_id(u): 
    return (u//64) % 256


def unique_channel_id(d): 
    return((d['io_group'].astype(int)*256+d['io_channel'].astype(int))*256 
           + d['chip_id'].astype(int))*64 + d['channel_id'].astype(int)


def parse_file(filename):
    """
    Reads the .h5 file from the pedestal run and turns it into a readable format.

    Parameters
    ----------
    filename : str
        Name of the pedestal file.

    Returns
    -------
    d : dict
        Contains the ADC mean, standard, and rate of each channel.

    """
    d = dict()
    f = h5py.File(filename,'r')
    unixtime=f['packets'][:]['timestamp'][f['packets'][:]['packet_type']==4]
    livetime = np.max(unixtime)-np.min(unixtime)
    data_mask = f['packets'][:]['packet_type']==0
    valid_parity_mask = f['packets'][:]['valid_parity']==1
    mask = np.logical_and(data_mask, valid_parity_mask)
    adc = f['packets']['dataword'][mask]
    unique_id = unique_channel_id(f['packets'][mask])
    unique_id_set = np.unique(unique_id)
    for i in unique_id_set:
        id_mask = unique_id == i
        masked_adc = adc[id_mask]
        d[i]=dict(
            mean = np.mean(masked_adc),
            std = np.std(masked_adc),
            rate = len(masked_adc) / (livetime + 1e-9) )
    return d


def plot_xy(d, metric, tile_id):
    """
    Creates a 2d histogram of the ADC for each channel.

    Parameters
    ----------
    d : dict
        Dictionary produced by parse_file.
    metric : str
        Metric of ADC to plot. Options are mean, std, and rate.
    tile_id : int
        Id of the tile.

    Returns
    -------
    None.

    """
    geometry_yaml = 'layout-2.2.1.yaml'
    with open(geometry_yaml) as fi: geo = yaml.full_load(fi)
    pitch = 4.434

    chip_pix = dict((geo['chips'][i][0], geo['chips'][i][1]) for i in range(len(geo['chips'])))

    ch_vertical_lines=np.linspace(-1*(geo['width']/2), geo['width']/2, 22)
    ch_horizontal_lines=np.linspace(-1*(geo['height']/2), geo['height']/2, 22)

    vertical_lines=np.linspace(-1*(geo['width']/2), geo['width']/2, 4)
    horizontal_lines=np.linspace(-1*(geo['height']/2), geo['height']/2, 4)

    nonrouted_v2a_channels=[6,7,8,9,22,23,24,25,38,39,40,54,55,56,57]
    routed_v2a_channels=[i for i in range(64) if i not in nonrouted_v2a_channels]

    fig, ax = plt.subplots(figsize=(10,8))
    ax.set_xlabel('X Position [mm]'); ax.set_ylabel('Y Position [mm]')
    ax.set_xticks(vertical_lines); ax.set_yticks(horizontal_lines)
    ax.set_xlim(vertical_lines[0]*1.1, vertical_lines[-1]*1.1)
    ax.set_ylim(horizontal_lines[0]*1.1, horizontal_lines[-1]*1.1)

    for vl in vertical_lines:
        ax.vlines(x=vl, ymin=horizontal_lines[0], ymax=horizontal_lines[-1], colors=['k'], linestyle='solid')
    for hl in horizontal_lines:
        ax.hlines(y=hl, xmin=vertical_lines[0], xmax=vertical_lines[-1], colors=['k'], linestyle='solid')
        
    for chvl in ch_vertical_lines:
        ax.vlines(x=chvl, ymin=ch_horizontal_lines[0], ymax=ch_horizontal_lines[-1], colors=['k'], alpha=0.15)
    for chhl in ch_horizontal_lines:
        ax.hlines(y=chhl, xmin=ch_vertical_lines[0], xmax=ch_vertical_lines[-1], colors=['k'], alpha=0.15)

    chipid_pos = dict()
    for chipid in chip_pix.keys():
        x,y = [[] for i in range(2)]
        for channelid in routed_v2a_channels:
            x.append( geo['pixels'][chip_pix[chipid][channelid]][1] )
            y.append( geo['pixels'][chip_pix[chipid][channelid]][2] )
        avgX = (max(x)+min(x))/2.
        avgY = (max(y)+min(y))/2.
        chipid_pos[chipid]=dict(minX=min(x), maxX=max(x), avgX=avgX, minY=min(y), maxY=max(y), avgY=avgY)
        plt.annotate(str(chipid), [avgX,avgY], ha='center', va='center')

    valid_chip_ids = [14, 13, 12, 24, 23, 22, 34, 33, 32]
    for key in d.keys():
        channel_id = find_channel_id(key)
        chip_id = find_chip_id(key)
        if chip_id not in valid_chip_ids: continue
        if channel_id in nonrouted_v2a_channels: continue
        if channel_id not in range(64): continue
        x = geo['pixels'][chip_pix[chip_id][channel_id]][1]
        y = geo['pixels'][chip_pix[chip_id][channel_id]][2]
        
        if metric=='mean':
            normalization=40
        if metric=='std':
            normalization=10
        if metric=='rate':
            normalization=2
        
        weight = d[key][metric]/normalization
        # if weight > 1: weight = 0.9999
        r = Rectangle((x-(pitch/2.), y-(pitch/2.)), pitch, pitch, color=cm.YlGnBu(weight))
        plt.gca().add_patch( r )

    colorbar = fig.colorbar(cm.ScalarMappable(norm=Normalize(vmin=0, vmax=normalization), cmap='YlGnBu'), ax=ax)

    if metric=='mean':
        ax.set_title('ADC Mean')
        colorbar.set_label('[ADC]')
        plt.savefig('tile-id-'+str(tile_id)+'-xy-mean.png')
    if metric=='std':
        ax.set_title('ADC RMS')
        colorbar.set_label('[ADC]')
        plt.savefig('tile-id-'+str(tile_id)+'-xy-std.png')
    if metric=='rate':
        ax.set_title('Trigger Rate')
        colorbar.set_label('[Hz]')
        plt.savefig('tile-id-'+str(tile_id)+'-xy-rate.png')
        

def plot_adc_trigger(filename):
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
    f = h5py.File(filename,'r')

    fig, ax = plt.subplots(3,3, figsize=(32, 16), sharex=True)
    fig.set_tight_layout(True)

    df = pd.DataFrame(f['packets'][:])
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]

    nonrouted_v2a_channels=[6,7,8,9,22,23,24,25,38,39,40,54,55,56,57]
    routed_v2a_channels=[i for i in range(64) if i not in nonrouted_v2a_channels]
    cids = [12, 13, 14, 22, 23, 24, 32, 33, 34]

    for i in range(len(cids)):
        chip = df.loc[df['chip_id'] == cids[i]]
        labels, colors = [], []
        for chan_id in routed_v2a_channels:
            channel = chip.loc[chip['channel_id']==chan_id]
            channel = list(channel['dataword'])
            weight = chan_id/64
            
            ax[i%3][i//3].hist(channel, bins = np.linspace(0, 100, 101), log=True, histtype=u'step',
                               alpha = 0.8, color=cm.viridis(weight), lw = 0.5)
            ax[i%3][i//3].grid(alpha = 0.5)
            
            if channel.count(255) > 0.5*len(channel):
                labels.append(chan_id)
                colors.append(cm.viridis(weight))
        
        lines = [Line2D([0], [0], color=colors[i]) for i in range(len(colors))]
        
        ax[i%3][i//3].set_title(f'chip {cids[i]}', fontsize = '6')
        ax[i%3][i//3].set_xlabel('ADC', fontsize = '6')
        ax[i%3][i//3].set_ylabel('trigger count', fontsize = '6')
        ax[i%3][i//3].legend(lines, labels, loc='upper left', fontsize="6")
        ax[i%3][i//3].tick_params(axis='both', labelsize=6)
        plt.savefig('adc_trigger.png')
        
        
def plot_adc_time(filename):
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
    f = h5py.File(filename,'r')

    df = pd.DataFrame(f['packets'][:])
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]
    cids = [12, 13, 14, 22, 23, 24, 32, 33, 34]

    nonrouted_v2a_channels=[6,7,8,9,22,23,24,25,38,39,40,54,55,56,57]
    routed_v2a_channels=[i for i in range(64) if i not in nonrouted_v2a_channels]

    fig, ax = plt.subplots(3, 3, figsize=(32, 16), sharex = True, sharey=True)
    fig.set_tight_layout(True)
    markers = ['.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']

    for i in range(len(cids)):
        chip = df.loc[df['chip_id'] == cids[i]]
        min_time = min(chip['timestamp'])
        for ch in range(len(routed_v2a_channels)):
            channel = chip.loc[chip['channel_id']==routed_v2a_channels[ch]]
            adc = list(channel['dataword'][:])
            time = [i - min_time for i in list(channel['timestamp'][:])]
            weight = routed_v2a_channels[ch]/64
            ax[i%3][i//3].scatter(time, adc, color=cm.viridis(weight), 
                               alpha = 0.9, marker = markers[ch%15], s = 0.7)
            ax[i%3][i//3].plot(time, adc, color=cm.viridis(weight), 
                               alpha = 0.9, lw = 0.5)
            
        ax[i%3][i//3].set_title(f'chip {cids[i]}', fontsize='6')
        ax[i%3][i//3].tick_params(axis='both', labelsize=6)
        ax[i%3][i//3].set_xlabel('Time [0.1 us]', fontsize='6')
        ax[i%3][i//3].set_ylabel('ADC', fontsize='6')
        ax[i%3][i//3].grid(alpha = 0.5)

    plt.savefig('adc_time.png')
    
    
def channel_colors():
    """
    Creates a plot color coding the channels on a chip.

    Returns
    -------
    None.

    """
    channel_array = np.array([[ 3,  2,  1, 63, 62, 61, 60],
                              [10,  5,  4,  0, 59, 58, 52],
                              [13, 12, 11, 49, 50, 51, 53],
                              [17, 16, 15, 14, 46, 47, 48],
                              [20, 21, 18, 42, 43, 44, 45],
                              [19, 26, 27, 32, 36, 37, 41],
                              [28, 29, 30, 31, 33, 34, 35]])

    fig, ax = plt.subplots(figsize=(10,8))
    ax.axis('off')

    vertical_lines=np.linspace(-0.5, 6.5, 8)
    horizontal_lines=np.linspace(-6.5, 0.5, 8)

    for vl in vertical_lines:
        ax.vlines(x=vl, ymin=horizontal_lines[0], ymax=horizontal_lines[-1], colors=['k'], linestyle='solid')
    for hl in horizontal_lines:
        ax.hlines(y=hl, xmin=vertical_lines[0], xmax=vertical_lines[-1], colors=['k'], linestyle='solid')

    for channel_col in range(len(channel_array)):
        for channel_row in range(len(channel_array[channel_col])):
            x = channel_row
            y = -channel_col
            weight = channel_array[channel_col][channel_row]/64
            ax.text(x, y, channel_array[channel_col][channel_row], va='center', ha='center')
            r = Rectangle((x-0.5, y-0.5) , 1, 1, color=cm.viridis(weight))
            plt.gca().add_patch(r)

    fig.colorbar(cm.ScalarMappable(norm=Normalize(vmin=0, vmax=64), cmap='viridis'), ax=ax)
    plt.savefig('channel_colors.png')
    