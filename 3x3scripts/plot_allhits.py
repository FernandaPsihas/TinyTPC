# import matplotlib.pyplot as plt
# import pandas as pd
# import h5py
# import numpy as np
# from matplotlib.colors import Normalize
# import argparse
# import seaborn as sns
# from matplotlib.colors import LogNorm, Normalize
# import matplotlib.cm as cm
# from matplotlib.backends.backend_pdf import PdfPages
# import os
# import scipy

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
import scipy

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

def parse_json(json_filename):
    f = open(json_filename)

    off = []
    for line in f:
        if 'channel_mask' in line:
            for i in line:
                if i == '1' or i == '0':
                    off.append(int(i))
    return off


def ADCs_to_charge(ADCs):
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

    charges = []
    for ADC in ADCs:
        pkt_charge = ADC*((vref-vcm)/256)/gain
        charges.append(pkt_charge)
    return charges



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
    filename = 'pedestal_8-20.txt'
    #filename = 'pedestal_8-22.txt'
    #filename = 'pedestal_8-18.txt'
    #filename = 'pedestal_8-21.txt'
    x = np.genfromtxt(filename)
    return x


############################

def get_hits(df, start_time, end_time, hits, file_hits, times, es):

    chip13 = df.loc[df['chip_id'] == 13]
    min_time = min(chip13['timestamp'])

    # Channel map (do not edit)
    channel_array = np.array([[28, 19, 20, 17, 13, 10,  3],
                              [29, 26, 21, 16, 12,  5,  2],
                              [30, 27, 18, 15, 11,  4,  1],
                              [31, 32, 42, 14, 49,  0, 63],
                              [33, 36, 43, 46, 50, 59, 62],
                              [34, 37, 44, 47, 51, 58, 61],
                              [35, 41, 45, 48, 53, 52, 60]])
    # Chip map (do not edit)
    chip_array = np.array([[12, 13, 14],
                           [22, 23, 24],
                           [32, 33, 34]])

    # # Make 2D arrays for 2D plot data
    adc_data = np.arange(441).reshape((21, 21))
    time_data = np.arange(441).reshape((21, 21))
    masked_data = np.arange(441).reshape((21, 21))

    # Look for hits in this time window
    df_cut = df[(df['timestamp']-min_time).between(start_time*1e7, (end_time)*1e7)]

    #    dit = channel_mask()
    ped = read_pedestal()

    i = 0
    time_lst = []
    hit_lst = []
    e_lst = []
    adc_lst = []
    for chip_lst in chip_array:
        for channel_lst in channel_array:
            for chip_id in chip_lst:
                chip = df_cut.loc[df_cut['chip_id'] == chip_id]
                a, b = np.where(chip_array == chip_id)
                c = 2*a[0]+b[0]

                # if chip_id in dit.keys():
                #     masked = dit[chip_id]
                # else:
                #     masked = None
                masked = None

                for channel_id in range(len(channel_lst)):
                    x = int(i/3)
                    y = (i*7)%21 + channel_id

                    channel = chip.loc[chip['channel_id']==channel_lst[channel_id]]

                    adc = list(channel['dataword'])
                    time = list(channel['timestamp'])
                    time = [t - min_time for t in time]

                    masked_data[x][y] = 0
                    # if masked != None:
                    #     masked_data[x][y] = masked[channel_lst[channel_id]]
                    # else:
                    #     masked_data[x][y] = 0

                    if len(adc) == 0:
                        adc_data[x][y] = 0
                        time_data[x][y] = 0
                    else:
                        #print(time)
                        hit_lst.extend(adc - ped[x][y]) #substract pedestal
                        time_lst.extend(time)
                        e_lst=ADCs_to_charge(hit_lst)
                i += 1
    es.extend(e_lst)
    file_hits.extend(hit_lst)
    hits.extend(hit_lst)
    times.extend(time_lst)



def main(filenames, hit_cut=10):
    time_bins = 10000
#'pedestal_8-20.txt'
    event_times_highE = []
    event_times_noise = []
    # make plot of hit_adc
    hits_charge = []
    hits = []
    times = []
    hits_charge_noise = []
    hits_noise = []
    times_noise = []
    fig_nums = []
    # f = []
    # date = []
    # for i in files:
    #     f.append(h5py.File(filename, 'r'))
    #     date.append(filename[13:])
     # for i in range(4):
    # file_hits = []
    # file_hits_noise = []
    for filename in filenames:
        # print("Number of hits1:", len(file_hits))
        # Process each filename here
        file_hits = []
        file_hits_noise = []
        # print("Number of hits2:", len(file_hits))
        print("Processing file:", filename,"\n")
        # print("Number of hits3:", len(file_hits))
        f = h5py.File(filename, 'r')
        date = filename[13:]
        # print('Date first: ', date)
        date = f'{date[5:7]}_{date[8:10]}_{date[11:13]}-{date[14:16]}-{date[17:19]}'
        # print('Second first: ', date)

        df = pd.DataFrame(f['packets'][:])
        df = df.loc[df['packet_type'] == 0]
        df = df.loc[df['valid_parity'] == 1]

        # print("df:", df)

        #Checking if the file contains valid data
        if df.empty:
            print("Skipping file:", filename, "as it has no valid data. \n")
            continue

        #Check if the desired chip id contains valid data
        chip13 = df.loc[df['chip_id'] == 13]
        # print("Length of chip12 DataFrame:", len(chip12))  # Print length of chip12 DataFrame

        if chip13.empty:
            print("No data for chip_id == 13 in file:", filename, "\n")
            continue

        min_time = min(chip13['timestamp'])
        # print("Minimum time:", min_time)

        time = [t - min_time for t in df['timestamp']]

        max_time = max(time)
        bin_size = int(max_time / time_bins)

        for i in range(0, time_bins): # loop over all events (time windows)
            t_min = bin_size*i
            t_max = bin_size*(i+1)
            cut_df = df[(df['timestamp']-min_time).between(t_min, t_max)]
            if len(cut_df)>hit_cut: # save times where hits are >hit_cut max hits (change to < )
                event_times_highE.append([t_min, t_max])
            else:
                if len(cut_df)>0:
                    event_times_noise.append([t_min, t_max])
                # append df['dataword'] to hit_hit_cut array


        for i in range(len(event_times_highE)):
            start_time = event_times_highE[i][0]/1e7
            end_time = event_times_highE[i][1]/1e7
            #plot_xy_selected(filename, start_time, end_time)
            get_hits(df, start_time, end_time, hits, file_hits, times, hits_charge)
            # fig_nums.append(plt.gcf().number)
            #print(i+1, 'done!')

        for i in range(len(event_times_noise)):
            start_time = event_times_noise[i][0]/1e7
            end_time = event_times_noise[i][1]/1e7
            #plot_xy_selected(filename, start_time, end_time)
            get_hits(df, start_time, end_time, hits_noise, file_hits_noise, times_noise, hits_charge_noise)
            # fig_nums.append(plt.gcf().number)
            #print(i+1, 'done!')
        # break
        print("Hits in file: ", filename, "is ", len(file_hits))
        print("Total hits until now is: ", len(hits))

    # print('hits')
    # print(hits, "\n")
    # print('es')
    # print(hits_charge, "\n")
    # print('times')
    # print(len(times), "\n")


    #start plotting

    fig, ax = plt.subplots(figsize=(10,8))
    ax.set_xlabel('time')
    ax.set_ylabel('hits')
    plt.hist(times, 20,histtype='step', fill=False, label='>= 10 hits (in 10 drifts)')
    plt.hist(times_noise,20, histtype='step', fill=False, label=' < 10 hits (in 10 drifts)')
    ax.set_title('timestamps in 2024_07_08_22-11_CT')
    plt.legend()
    plt.text(0.2, 1.02, '4kV data', horizontalalignment='right',verticalalignment='center', transform=ax.transAxes,fontsize=15,color="#a50d31")
    plt.savefig('4kV - 2024_07_08_22-11_CT'+'--time.png')
    #plt.savefig('tile-id-'+str(tile_id)+'-xy-mean.png')
    #plt.show()

    fig, ax = plt.subplots(figsize=(10,8))
    ax.set_xlabel('ADC');
    ax.set_ylabel('hits')
    plt.hist(hits, 30,histtype='step', fill=False, label='>= 10 hits (in 10 drifts)')
    plt.hist(hits_noise,30, histtype='step', fill=False, label=' < 10 hits (in 10 drifts)')
    ax.set_title('Pedestal-substracted ADC in 2024_07_08_22-11_CT')
    plt.legend()
    plt.text(0.2, 1.02, '4kV data ', horizontalalignment='right',verticalalignment='center', transform=ax.transAxes,fontsize=15,color="#a50d31")
    plt.savefig('4kV- 2024_07_08_22-11_CT'+'--ADC.png')
    #plt.show()


    fig, ax = plt.subplots(figsize=(10,8))
    ax.set_xlabel('ke');
    ax.set_ylabel('hits')
    plt.hist(hits_charge, 30, density=True,histtype='step', fill=False, label='>= 10 hits (in 10 drifts)')
    plt.hist(hits_charge_noise,30, density=True, histtype='step', fill=False, label=' < 10 hits (in 10 drifts)')
    ax.set_title('Charge in 2024_07_08_22-11_CT')
    plt.legend()
    plt.text(0.2, 1.02, '4kV data', horizontalalignment='right',verticalalignment='center', transform=ax.transAxes,fontsize=15,color="#a50d31")
    #plt.show()
    plt.savefig('4kV 2024_07_08_22-11_CT'+'--charge.png')

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlabel('ke');
    ax.set_ylabel('Timestamp')
    # Create 2D histogram for hits_charge
    plt.hist2d(hits_charge, times, bins=30, density=True, cmap='Blues', label='>= 10 hits (in 10 drifts)')
    # Create 2D histogram for hits_charge_noise
    # plt.hist2d(times_noise, hits_charge_noise, bins=30, density=True, cmap='Reds', label='< 10 hits (in 10 drifts)')
    ax.set_title('Electron Count vs time in 2024_07_08_22-11_CT')
    plt.colorbar(label='Density')
    # plt.legend()
    plt.text(0.2, 1.02, '4kV data', horizontalalignment='right', verticalalignment='center', transform=ax.transAxes,
             fontsize=15, color="#a50d31")
    plt.savefig('2024_07_08_22-11_CT' + '-- ke vs time.png')

    #check for 20-25k electron count
    ke = []

    for i in hits_charge:
        if 18 <= i <= 27:
            ke.append(i)

    print("Electron counts in the 18k - 27k region:", ke)

def flenmes_from_fle(filename):
    with open(filename, 'r') as file:
        filenames = [line.strip() for line in file.readlines()]
    return filenames


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filelist', type=str, help='Text file with list of hdf5 files')
    parser.add_argument('--hit_cut', default=10, type=int, help='nhit cutoff for potential tracks (default = 10)')
    args = parser.parse_args()

    if args.filelist:
        filenames = flenmes_from_fle(args.filelist)
    else:
        raise ValueError("No input files specified. Please provide a text file with list of hdf5 files using --filelist")

    main(filenames, args.hit_cut)