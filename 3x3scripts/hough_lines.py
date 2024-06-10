import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
# from skimage.transform import hough_line, hough_line_peaks
# from skimage.feature import canny
# from skimage.draw import line as draw_line
# from skimage import data
# import matplotlib.cm as cm
from skimage.transform import probabilistic_hough_line
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from tqdm import tqdm


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


def array_2d(df):
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

    i = 0
    dit = channel_mask()
    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                chip = df.loc[df['chip_id'] == chip_id]

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
                    
                    if masked != None:
                        masked_data[x][y] = masked[channel_lst[channel_id]]
                    else:
                        masked_data[x][y] = 0
                        
                    if len(adc) == 0:
                        adc_data[x][y] = 0
                        time_data[x][y] = 0
                    else:
                        adc_data[x][y] = np.median(adc)
                        time_data[x][y] = np.median(time)
                i += 1
    
    return adc_data, time_data, masked_data


def draw_line(mat, x0, y0, x1, y1):
    if x0 > x1:
        x0, y0, x1, y1 = x1, y1, x0, y0
    mat[x0, y0] = 1
    mat[x1, y1] = 1
    
    x = np.arange(x0 + 1, x1)
    if x1 == x0:
        y = 0
    else:
        y = np.round(((y1 - y0) / (x1 - x0)) * (x - x0) + y0).astype(x.dtype)
    mat[x, y] = 1
    
    for line in range(len(mat)):
        for item in range(len(mat[0])):
            if mat[line][item] == 1:
                if item != 0:
                    mat[line][item-1] += 1
                if mat[line][item-2] == 1: continue
                else:
                    if item != 20:
                        mat[line][item+1] +=1
    return mat 


def line2(mat, x):
    for line in range(len(mat)):
        for item in range(len(mat[0])):
            if item == x:
                mat[line][item] += 1
            if item == x+1:
                mat[line][item] += 1
    return mat
    


def hough_lines(array, leng, date = '', event = 0):
    # edges = canny(array)
    lines = probabilistic_hough_line(array, line_length=3,
                                      line_gap=3)
    fig, ax = plt.subplots(1, 2, figsize=(7, 4))
    fig.set_tight_layout(True)
    
    for i in range(2):
        ax[i].axis('off')
        ax[i].hlines([0, 7, 14, 21], 0, 21, color = 'black', lw = 1)
        ax[i].vlines([0, 7, 14, 21], 0, 21, color = 'black', lw = 1)
    
    data_mask = array == 0
    sns.heatmap(array, mask = data_mask, vmin = 0, cmap = 'plasma_r', cbar = False, 
                    linewidths = 0.1, ax=ax[0], linecolor='darkgray')
    sns.heatmap(array, mask = data_mask, vmin = 0, cmap = 'plasma_r', cbar = False,
                    linewidths = 0.1, ax=ax[1], linecolor='darkgray')
    
    ax[1].set_ylim((array.shape[0], 0))
    ax[1].set_axis_off()
    ax[1].set_title('Detected lines')
    
    ax[0].set_ylim((array.shape[0], 0))
    ax[0].set_axis_off()
    ax[0].set_title('Data')
    
    mat = np.zeros(441).reshape((21, 21))
    if len(lines) == 1:
        p0, p1 = lines[0]
        y0, x0 = p0
        y1, x1 = p1
        if p1[1] - p0[1] == 0:
            slope = 0.0
        else:
            slope =(p1[0]-p0[0])/(p1[1]-p0[1])
        # dist = np.sqrt((p1[0]-p0[0])**2 + (p1[1]-p0[1])**2)
        angle = np.arctan(slope)*180/np.pi

        mat = draw_line(mat, x0, y0, x1, y1)
    
        data_mask = mat == 0
        sns.heatmap(mat, mask = data_mask, vmin = 0, vmax = 3, cmap = 'binary', cbar = False,
                        linewidths = 0.1, ax=ax[1], linecolor='darkgray', alpha = 0.8)
        
        no = 0
        for line in range(len(mat)):
            for item in range(len(mat[0])):
                if mat[line][item] == 0 and array[line][item] != 0:
                    no += 1
        
        acc = no/leng
        plt.suptitle(f'{date[:2]}/{date[3:5]} {date[6:8]}:{date[9:11]}:{date[12:]}\nevent {event+1}\n{len(lines)} hough lines\naccuracy {round((1-acc)*100, 2)}%')
    
    elif len(lines) == 0:
        mat = np.zeros(441).reshape((21, 21))
        for i in range(21):
            mat = line2(mat, i)
            no = 0
            for line in range(len(mat)):
                for item in range(len(mat[0])):
                    if mat[line][item] == 0 and array[line][item] != 0:
                        no += 1
            acc = no/leng
            if acc == 0.0:
                data_mask = mat == 0
                sns.heatmap(mat, mask = data_mask, vmin = 0, vmax = 3, cmap = 'binary', cbar = False,
                                linewidths = 0.1, ax=ax[1], linecolor='darkgray', alpha = 0.8)
                plt.suptitle(f'{date[:2]}/{date[3:5]} {date[6:8]}:{date[9:11]}:{date[12:]}\nevent {event+1}\n{len(lines)} hough lines\naccuracy {round((1-acc)*100, 2)}%')
                angle = 0
                break
            else:
                mat = np.zeros(441).reshape((21, 21))
                acc = None
                angle = None
                plt.suptitle(f'{date[:2]}/{date[3:5]} {date[6:8]}:{date[9:11]}:{date[12:]}\nevent {event+1}\n{len(lines)} hough lines')
    
    else:
        for line in lines:
            p0, p1 = line
            ax[1].plot((p0[0], p1[0]), (p0[1], p1[1]), color = 'blue', lw = 3)
        acc = None
        angle = None
        plt.suptitle(f'{date[:2]}/{date[3:5]} {date[6:8]}:{date[9:11]}:{date[12:]}\nevent {event+1}\n{len(lines)} hough lines')
    # plt.savefig(f'houghs_{date}_{event}.png')
    return len(lines), acc, angle

file_lst = []
files = os.listdir()
for filename in files:
    if 'events_02' in filename:
        if 'hough_' in filename:
            continue
        else:
            file_lst.append(filename)
        

file_lst = sorted(file_lst)
print(len(file_lst), 'files to read')


select = []
for filename, t in zip(file_lst, tqdm(range(len(file_lst)))):
# for filename in file_lst:
    date = filename[7:-3]
    df = pd.read_hdf(filename)
    saved_df = pd.DataFrame()
    # print(max(df['n_event']))
    if max(df['n_event']) > 20:
        print('too many events!!')
    else:
        fig_nums_1 = []
        fig_nums_oth = []
        n_sel = 0
        for i in range(max(df['n_event'])+1):
            eve = df.loc[df['n_event'] == i]
            adc_data, time_data, masked_data = array_2d(eve)
            n_lines, acc, angle = hough_lines(time_data, len(eve), date, event = i)
            
            if n_lines == 1 and acc != None and acc < 0.25:
                angles = pd.Series([angle for x in range(len(eve))], name = 'angle', index = eve.index)
                event = pd.concat([eve, angles], axis = 1)
                saved_df = pd.concat([saved_df, event], axis = 0)

            elif n_lines == 0 and acc != None and acc == 0.0:
                angles = pd.Series([0.0 for x in range(len(eve))], name = 'angle', index = eve.index)
                event = pd.concat([eve, angles], axis = 1)
                saved_df = pd.concat([saved_df, event], axis = 0)
        
                   
            if n_lines == 1 and acc != None and acc < 0.25:
                fig_nums_1.append(plt.gcf().number)
                n_sel += 1
            elif n_lines == 0 and acc != None and acc == 0.0:
                fig_nums_1.append(plt.gcf().number)
                n_sel += 1
            else:
                fig_nums_oth.append(plt.gcf().number)
        
        select.append(n_sel)
        
        p1 = PdfPages(f'hough_one_{date}.pdf') 
        po = PdfPages(f'hough_other_{date}.pdf') 
    
        figs_1 = [plt.figure(n) for n in fig_nums_1] 
        figs_o = [plt.figure(n) for n in fig_nums_oth] 
        
        if len(figs_1) == 0:
            continue
        elif len(figs_o) == 0:
            continue
        else:
            for fig in figs_1:  
                fig.savefig(p1, format='pdf')
            for fig_o in figs_o:
                fig_o.savefig(po, format='pdf') 
            plt.close('all')  
            p1.close()
            po.close()
            
            output_filename = f'hough_events_{date}.h5'
            saved_df.to_hdf(output_filename, key='df', mode='w') 
            
            # print(filename, '->', output_filename, 'finished!')
        pass

# plt.close('all')
# fig, ax = plt.subplots(figsize=(9, 4))
# ax.hist(select, histtype=u'step')
# ax.set_title('Muon Tracks Histogram')
# ax.set_xlabel('no. of muons')
# ax.set_ylabel('count')
# plt.savefig('muon_hist.png')



