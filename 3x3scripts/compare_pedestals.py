import matplotlib.pyplot as plt
import yaml
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import pedestal_plots


def compare_pedestals(filename1, filename2, metric):
    """
    Reads the .h5 file from the pedestal run and turns it into a readable format.

    Parameters
    ----------
    filename1 : str
        Name of the first pedestal file.
    filename2 : str
        Name of the second pedestal file.
    metric : str
	Metric of ADC to plot. Options are mean, std, or rate.

    Returns
    -------
    None

    """
    d1 = pedestal_plots.parse_file(filename1)
    d2 = pedestal_plots.parse_file(filename2)
    
    lst = []
    d = dict()
    for key in d1.keys():
        if key not in d2.keys() and d1.keys(): continue
        if float(d2[key][metric]) == 0: continue
        if float(d1[key][metric]) == 0: continue
        else:
            m = float(d1[key][metric])/float(d2[key][metric])
            lst.append(m)
            d[key]=dict(m)
    
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
    if metric == 'mean':
        ax.set_title('ADC Mean')
    if metric == 'std':
        ax.set_title('ADC RMS')
    if metric == 'rate':
        ax.set_title('Rate')
    
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
        channel_id = pedestal_plots.find_channel_id(key)
        chip_id = pedestal_plots.find_chip_id(key)
        if chip_id not in valid_chip_ids: continue
        if channel_id in nonrouted_v2a_channels: continue
        if channel_id not in range(64): continue
        x = geo['pixels'][chip_pix[chip_id][channel_id]][1]
        y = geo['pixels'][chip_pix[chip_id][channel_id]][2]
    
        weight = (d[key]-min(lst))/(max(lst)-min(lst))
        r = Rectangle((x-(pitch/2.), y-(pitch/2.)), pitch, pitch, color=cm.YlOrRd(weight))
        plt.gca().add_patch(r)
    
    colorbar = fig.colorbar(cm.ScalarMappable(norm=Normalize(vmin=min(lst), vmax=max(lst)), cmap='YlOrRd'), ax=ax)
    plt.savefig(f'compare_pedestal_xy_{metric}.png')
