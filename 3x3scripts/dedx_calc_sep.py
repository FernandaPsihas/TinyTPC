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
from matplotlib.patches import Arc
from tqdm import tqdm


V = 5 # in kV  ||| Rough Measurements for tinyTPC
d = 10 # in cm
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
# print(drift_time)


def read_pedestal():
    #add pedestal .txt file in manually here:
    filename = '/Users/hannahlemoine/3x3/2024_02_20_17-46_CT_2/pedestal_02_20_17_47_36.txt'
    x = np.genfromtxt(filename)
    
    return x


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

def plot(df):
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



def array_2d(df, filename = ''):
    angle1 = abs(list(df['angle'])[0])

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
    
    # dit = channel_mask()
    data_df = pd.DataFrame(columns=['x', 'y', 'adc', 'time', 'dx', 'dadcdx', 'angle1', 'angle2'])

    pedestal = read_pedestal()
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
                    time = list(channel['timestamp'])
                        
                    if len(adc) == 0:
                        adc_data[x][y] = 0
                        time_data[x][y] = 0
                    else:
                        adc_data[x][y] = np.median(adc) - pedestal[x][y]
                        time_data[x][y] = np.median(time)
                        
                        for v in range(len(adc)):
                            added = pd.DataFrame({'x' : [x],
                                                  'y': [y],
                                                  'adc': [adc[v]-pedestal[x][y]],
                                                  'time': [time[v]],
                                                  'dx': [0],
                                                  'dadcdx': [0],
                                                  'angle1': [angle1],
                                                  'angle2': [0]})
                            data_df = pd.concat([data_df, added])
                i += 1
    
    
    data_df = data_df.sort_values('time')
    data_df = data_df.set_index([pd.Index([i for i in range(len(data_df))])])
    
    indices = list(data_df.index)
    leng = 100/21 #mm

    vel = .16 #mm/0.1 us
    tot_dx = 0
    
    empty = [indices[-1]]
    for line in range(len(data_df)-1):
        x1 = data_df['x'][line]
        x2 = [data_df['x'][line+1]+1, data_df['x'][line+1], data_df['x'][line+1]-1]
        if x1 in x2:
            y1 = data_df['y'][line]
            y2 = [data_df['y'][line+1]+1, data_df['y'][line+1], data_df['y'][line+1]-1]
            if y1 in y2:                   
                
                if x1 == data_df['x'][line+1] and y1 == data_df['y'][line+1]:
                    # prev_time = data_df['time'][line]+data_df['time'][line+1]
                    # data_df.iloc[indices[line+1], 3] = prev_time
                    empty.append(line)
                    
                else:
                    dt = data_df['time'][line+1] - data_df['time'][line]
                    if dt > drift_time:
                        empty.append(line)
                    else:
                        dadc = data_df['adc'][line]
                        dx = dt*vel
                        # print(dt, dx)
                        tot_dx = dx+tot_dx
                        
                        z0 = 100 - ((x1*leng) + leng/2)
                        x0 = (data_df['time'][line])*vel
                        
                        x1 = (data_df['time'][line+1])*vel
                        z1 = 100 - ((data_df['x'][line+1]*leng) + leng/2)
                        
                        b1, a1 = np.polyfit([x0, x1], [z0, z1], deg=1)
                        
                        angle2 = abs(np.arctan(b1))
                        dz = abs(dx*b1)
                        if angle1 == 0.0:
                            dy = 0
                        else:
                            dy = dz/(np.tan(np.deg2rad(angle1)))
                            
                        dr = np.sqrt(dx**2 + dy**2 + dz**2)
                        if dr == 0:
                            empty.append(line)
                        else:
                            dadcdx = dadc/dr
                            
                            data_df.iloc[indices[line], 4] = dr
                            data_df.iloc[indices[line], 5] = dadcdx
                            data_df.iloc[indices[line], 7] = angle2
            else:
                empty.append(line)
        else:
            empty.append(line)
    
    data_df = data_df.drop(index = empty)
    data_df = data_df.set_index([pd.Index([i for i in range(len(data_df))])])
    return data_df, angle1


files = os.listdir()
file_lst = []
for file in files:
    if 'hough_even' in file:
        file_lst.append(file)

file_lst = sorted(file_lst)

all_data_0 = pd.DataFrame(columns=['x', 'y', 'adc', 'dx', 'dadcdx'])
all_data_oth = pd.DataFrame(columns=['x', 'y', 'adc', 'dx', 'dadcdx'])

for filename, i in zip(file_lst, tqdm(range(len(file_lst)))):
    df = pd.read_hdf(filename)
    df.dropna(inplace=True)
    
    if len(df) == 0:
        continue
    else:
        # print(filename)
        n_events = df.n_event.unique()
        for event in n_events:

            data, angle = array_2d(df.loc[df['n_event'] == event], f'{filename}, event {event}')

            if type(data) != int:
                if angle == 0.0:
                    all_data_0 = pd.concat([all_data_0, data])
                else:
                    all_data_oth = pd.concat([all_data_oth, data])
                    
    pass


all_data_0 = all_data_0.set_index([pd.Index([i for i in range(len(all_data_0))])])
all_data_oth = all_data_oth.set_index([pd.Index([i for i in range(len(all_data_oth))])])

# print(all_data)

fig, ax = plt.subplots(2, 3, figsize=(12, 8), sharey = True)
fig.set_tight_layout(True)

for i in range(0, 2):
    for j in range(3):
        ax[i][j].grid(alpha = .5)
        ax[i][j].set_ylabel('Count')
        
    ax[i][0].set_xlabel('dADC/dx')
    ax[i][0].set_title('dADC/dx')
    
    ax[i][2].set_xlabel('dx [mm]')
    ax[i][2].set_title('dx')
    
    ax[i][1].set_xlabel('dADC')
    ax[i][1].set_title('dADC')

dadcdx_0 = list(all_data_0['dadcdx'])
dadc_0 = list(all_data_0['adc'])
dx_0 = list(all_data_0['dx'])

ax[0][0].hist(dadcdx_0, histtype=u'step',
            bins = np.linspace(0, 40, 41), label = 'angle = 0')
ax[0][1].hist(dadc_0, histtype=u'step',
            bins = np.linspace(40, 120, 41), label = 'angle = 0')  
ax[0][2].hist(dx_0, histtype=u'step',
            bins = np.linspace(0, 25, 26), label = 'angle = 0')

dadcdx_oth = list(all_data_oth['dadcdx'])
dadc_oth = list(all_data_oth['adc'])
dx_oth = list(all_data_oth['dx'])

ax[0][0].hist(dadcdx_oth, histtype=u'step',
            bins = np.linspace(0, 40, 41), color = 'C1', label = 'angle != 0')
ax[0][1].hist(dadc_oth, histtype=u'step',
            bins = np.linspace(40, 120, 41), color = 'C1', label = 'angle != 0')  
ax[0][2].hist(dx_oth, histtype=u'step',
            bins = np.linspace(0, 25, 26), color = 'C1', label = 'angle != 0')

dadcdx = dadcdx_0+dadcdx_oth
dadc = dadc_0+dadc_oth
dx = dx_0+dx_oth

ax[1][0].hist(dadcdx, histtype=u'step',
            bins = np.linspace(0, 40, 41), color = 'C2', label = 'combined')
ax[1][1].hist(dadc, histtype=u'step',
            bins = np.linspace(40, 120, 41), color = 'C2', label = 'combined')  
ax[1][2].hist(dx, histtype=u'step',
            bins = np.linspace(0, 25, 26), color = 'C2', label = 'combined')

ax[0][0].legend()
ax[0][1].legend()
ax[0][2].legend()
ax[1][0].legend()
ax[1][1].legend()
ax[1][2].legend()
plt.show()   

plt.savefig('dedx_sep.png')
