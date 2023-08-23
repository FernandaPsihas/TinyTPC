#!/usr/bin/env python3

'''
Usage:

python3 event_display_whole_event.py CONVERTED_FILE

It will produce a pdf which contains the event display of the whole data-run, along with an interactive window. 

'''


import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
from struct import unpack
from mpl_toolkits.mplot3d import Axes3D
import random
import os
from matplotlib.ticker import MaxNLocator
import matplotlib as mp
import matplotlib.backends.backend_pdf

f = h5py.File(sys.argv[1],'r')

org = {
    '14': list(range(49)),  
    '13': list(range(49, 98)),  
    '12': list(range(98, 147)),
    '24': list(range(147,196)),
    '23': list(range(196, 245)),
    '22': list(range(245, 294)),
    '34': list(range(294,343)),
    '33': list(range(343, 392)),
    '32': list(range(392, 441)),   
}

unorg = [28, 29, 30, 31, 33, 34, 35, 19, 26, 27, 32, 36, 37, 41, 20, 21, 18, 42, 43, 44, 45, 17, 16, 15, 14, 46, 47, 48, 13, 12, 11, 49, 50, 51, 53, 10, 5, 4, 0, 59, 58, 52, 3, 2, 1, 63, 62, 61, 60]


channel_orgs = []
timestamp_orgs=[]
adc_orgs=[]
print(np.count_nonzero(f['packets'][:]['chip_id']), np.count_nonzero(f['packets'][:]['channel_id']))

for i in range(f['packets'][:]['chip_id'][:].size):
	data_packets_flag = f['packets'][:]['packet_type'][i]==0
	valid_parity_flag = f['packets'][:]['valid_parity'][i]==1
	data_flag = np.logical_and(data_packets_flag, valid_parity_flag)
	if f['packets'][:]['chip_id'][i]==0 or not data_flag:
		continue	
	else:
		timestamp_orgs.append(f['packets'][:]['timestamp'][i]/10**4)
		adc_orgs.append(f['packets']['dataword'][i])
		channel_item=0
		for item in range(len(unorg)):
			if unorg[item]==f['packets'][:]['channel_id'][i]:
				channel_item=item
				break
		for key in list(org.keys()):
			if key==f['packets'][:]['chip_id'][i].astype(str):
				channel_orgs.append(org[key][channel_item])
				break	

indices_orgs=np.argsort(timestamp_orgs)

timestamp_orgs_ind=[]
channel_orgs_ind=[]
adc_orgs_ind=[]
for ind in range(len(timestamp_orgs)):
	timestamp_orgs_ind.append(timestamp_orgs[indices_orgs[ind]])
	channel_orgs_ind.append(channel_orgs[indices_orgs[ind]])
	adc_orgs_ind.append(adc_orgs[indices_orgs[ind]])

timestamp_orgs_ind=np.array(timestamp_orgs_ind)
chann_pdf_to_vec=np.empty([22,22])
for j in range(22):
        for i in range(3):
                for k in range(7):
                        chann_pdf_to_vec[j,k + i*7]=(140 + 147*i -7*j + k)


data=[]
for ind in range(len(timestamp_orgs_ind)):
	for tot_ind in range(6000,67001):
		if timestamp_orgs_ind[ind] <= float(tot_ind + 1) and timestamp_orgs_ind[ind] >= float(tot_ind):
			flag_a = False
			for a in range (21):
				for b in range(21):
					if chann_pdf_to_vec[a,b]==channel_orgs_ind[ind]:
						data.append([a,b,tot_ind])
						flag_a = True
						break
				if flag_a:
					break
			break
		else:
			continue
	tot_ind = tot_ind + 1
 
data_x=[]
data_y=[]
data_z=[]
for i in range(3):
         x=0
         while x != len(data):
                 if i==0:
                         data_x.append(data[x][i])
                 elif i==1:
                         data_y.append(data[x][i])
                 else:
                         data_z.append(data[x][i])
                 x = x + 1
 
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.set_xlim(0, 21)
ax.set_ylim(0, 21)
ax.set_zlim(6000, 67001)
ax.set_zlabel('time [1 ms]')
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.zaxis.set_major_locator(MaxNLocator(integer=True))


norm = plt.Normalize(vmin=min(adc_orgs_ind), vmax=max(adc_orgs_ind))
ax.scatter(data_x, data_y, data_z, facecolors=plt.cm.plasma(norm(adc_orgs_ind)))
m = mp.cm.ScalarMappable(cmap=plt.cm.plasma, norm=norm)
plt.colorbar(m)
plt.show()

pdf = matplotlib.backends.backend_pdf.PdfPages('whole_event_for' + str(f) + '.pdf')
pdf.savefig(fig)
plt.close()
pdf.close()
f.close()
