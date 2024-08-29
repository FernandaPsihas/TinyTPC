import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
import os
import re
from tqdm import tqdm
from scipy import stats


dist = 100 #mm
vel = 0.1425 #mm/0.1 us 4kV

drift_time = (dist/vel)*1e7 #0.1 us
leng = 100/21


def read_pedestal(filename):
    x = np.genfromtxt(filename)
    return x


def convert_cm(df, ped):
    angle = list(df['angle'])[0]
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
    
    data_df = pd.DataFrame({'y': [0],
                            'z': [0],
                            'x': [0],
                            'adc': [0]})
    
    # vel = .01601 #cm/0.1us 5kV
    vel = 0.1425 #mm/0.1us
    leng = 100/21 #mm
    i = 0
    pedestal = read_pedestal(ped)
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
                        continue
                    else:
                        for t, a in zip(time, adc):
                            added = pd.DataFrame({'y': [(y*leng) + leng/2],
                                                  'z': [((20-x)*leng) + leng/2],
                                                  'x': [t*vel],
                                                  'adc': [a - pedestal[x][y]]})

                            data_df = pd.concat([data_df, added])
                i += 1
                
    data_df = data_df[data_df.adc != 0]  
    data_df = data_df.set_index([pd.Index([i for i in range(len(data_df))])])
          
    return data_df, angle


def dadcdx_calc(df, ped):
    points, angle = convert_cm(df, ped)

    if angle == 0.0:
        byz, ayz = 0, np.median(points['y'])
    else:
        byz, ayz = np.polyfit(points['y'], points['z'], deg=1)
    bxz, axz = np.polyfit(points['x'], points['z'], deg=1)

    squares_yz = pd.DataFrame({'ymin': [(i//21)*leng for i in range(441)], 
                        'ymax': [((i//21)*leng)+leng for i in range(441)],
                        'zmin': [(i%21)*leng for i in range(441)],
                        'zmax': [((i%21)*leng)+leng for i in range(441)]})

    data = pd.DataFrame({'x': [0],
                         'y': [0],
                         'dx': [0],
                         'dadcdx': [0]})
    
    for i in range(len(squares_yz)):
        ymin, ymax, zmin, zmax = squares_yz.iloc[i]
        square = points[points['z'].between(zmin, zmax)]
        square = square[square['y'].between(ymin, ymax)]
        if len(square) == 0: continue
        else:
            adc = np.median(square['adc'])

            incpt_yz = []
            if angle == 0.0:
                incpt_yz.append([np.median(points['y']), zmax])
                incpt_yz.append([np.median(points['y']), zmin])
            else:
                top = [(zmax-ayz)/byz, zmax]
                bottom = [(zmin-ayz)/byz, zmin]
                right = [ymax, ymax*byz + ayz]
                left = [ymin, ymin*byz + ayz]
            
                if 0.99999 < abs(byz) <= 1.00001:
                    incpt_yz.append([ymin, zmin])
                    incpt_yz.append([ymax, zmax])
                else:
                    if ymin <= top[0] <= ymax:
                        if zmin <= top[1] <= zmax:
                            incpt_yz.append(top)

                    if ymin <= bottom[0] <= ymax:
                        if zmin <= bottom[1] <= zmax:
                            incpt_yz.append(bottom)

                    if zmin <= left[1] <= zmax:
                        if ymin <= left[0] <= ymax:
                            incpt_yz.append(left)

                    if zmin <= right[1] <= zmax:
                        if ymin <= right[0] <= ymax:
                            incpt_yz.append(right)

            if len(incpt_yz) == 0: continue
            if len(incpt_yz) > 2: print('too many intercepts!!')
            else:
                line1 = incpt_yz[0][1]
                line2 = incpt_yz[1][1]
                
                incpt_xz = [[(line1-axz)/bxz, line1], [(line2-axz)/bxz, line2]]

                dx = incpt_xz[0][0] - incpt_xz[1][0]
                dy = incpt_yz[0][0] - incpt_yz[1][0]
                dz = incpt_yz[0][1] - incpt_yz[1][1]

                dr = np.sqrt(dx**2 + dy**2 + dz**2)
                if dr != 0:
                    dadcdx = adc/dr

                    added = pd.DataFrame({'x': [int(np.median(square['y']/leng) - 0.5)],
                                          'y': [int(np.median(square['z']/leng) - 0.5)],
                                          'dx': [dr],
                                          'dadcdx': [dadcdx]})
                    data = pd.concat([data, added])

    data = data[data.dx != 0]
    return data
                

direct = os.path.dirname(os.path.realpath(__file__))
os.chdir(direct) 

files = os.listdir()
pedestal = []
for filename in files:
    if filename.endswith(".txt"):
        if 'pedestal' in filename:
            pedestal.append(filename)

file_lst = []
for filename in files:
    if filename.endswith(".h5"):
        if 'hough_even' in filename:
                if 'events_08' in filename:
                    file_lst.append(filename)


all_data = pd.DataFrame({'x':[0],
                         'y': [0],
                         'dx': [0],
                         'dadcdx': [0],
                         'date': [0],
                         'event': [0]})

file_lst = sorted(file_lst)

for filename, i in zip(file_lst, tqdm(range(len(file_lst)))):
    df = pd.read_hdf(filename)
    regex = re.compile(r'\d{2}_\d{2}_\d{2}-\d{2}-\d{2}') 
    date = regex.search(filename).group()

    df.dropna(inplace=True)
    if len(df) == 0:
            continue
    else:
        n_events = df.n_event.unique()
        for event in n_events:
            eve = df.loc[df['n_event'] == event]
            data = dadcdx_calc(eve, pedestal[0])
            if type(data) != int:
                if len(data) != 0:
                    data['date'] = [date for i in data['dx']]
                    data['event'] = [event for i in data['dx']]
                    all_data = pd.concat([all_data, data])

all_data = all_data[all_data.date != 0]
all_data = all_data.set_index([pd.Index([i for i in range(len(all_data))])])

all_data.to_csv('dedx2.csv', index=False)

fig, ax = plt.subplots(1, 2, figsize=(12, 6), sharey = True)
fig.set_tight_layout(True)

for i in range(2):
    ax[i].grid(alpha = .5)
    ax[i].set_ylabel('count')

regex = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}-\d{2}') 
date = regex.search(direct).group()

plt.suptitle(f'{date[5:7]}/{date[8:10]}/{date[:4]},  dADC/dx\n4kV')
ax[0].set_xlabel('dADC/dx')
ax[0].set_title('dADC/dx')
    
ax[1].set_xlabel('dx [mm]')
ax[1].set_title('dx')

dadcdx = list(all_data['dadcdx'])
dx = list(all_data['dx'])
xmin = 0
xmax = 20
nbins = 21

# hist, bin_edges = np.histogram(dadcdx, bins=nbins, range=(xmin, xmax), density=True)

# params = stats.distributions.moyal.fit(dadcdx)
# loc, scale = params
# x = np.linspace(0, xmax, 1000)
# moyal_pdf = stats.moyal.pdf(x, loc, scale)

# # Scale Moyal PDF to match the histogram
# bin_width = (xmax - xmin) / nbins  # Adjust based on your histogram bins
# scaled_moyal_pdf = moyal_pdf * len(dadcdx) * bin_width

ax[0].hist(dadcdx, histtype=u'step',
            bins = np.linspace(xmin, xmax, nbins))
ax[1].hist(dx, histtype=u'step',
            bins = np.linspace(0, 25, 26))
    
# ax[0].axvline(x=np.median(dadcdx), color='red', linestyle='--', 
#             linewidth=2, label=f'Median: {np.median(dadcdx):.2f}')

# # Plot the fitted distribution
# ax[0].plot(x, scaled_moyal_pdf, 'k-', linewidth=2, label='Moyal fit')
ax[0].legend(loc = 'upper right')

plt.savefig('dedx_2d.png')

