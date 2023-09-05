import matplotlib.pyplot as plt
import pandas as pd
import h5py
import numpy as np

# filename = 'tile-id-tile-raw_2023_08_18_17_43_52_CDT_conv.h5'

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
    csa_gain = 4
    
    vref = VDDA*(vref_dac/265)
    vcm = VDDA*(vcm_dac/256)
    gain = 4 - 2*csa_gain
    pkt_charge = ADC*((vref-vcm)/256)/gain
    return pkt_charge


def plot_adc_all_trigger(filename):
    """
    Plots the ADC trigger rate and ADC vs. Time for all channels on all chips

    Parameters
    ----------
    filename : str
        Name of file

    Returns
    -------
    None.

    """
    f = h5py.File(filename,'r')
    fig, ax = plt.subplots(2, 1, figsize = (8, 8))
    
    df = pd.DataFrame(f['packets'][:])
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]
    
    nonrouted_v2a_channels=[6,7,8,9,22,23,24,25,38,39,40,54,55,56,57]
    routed_v2a_channels=[i for i in range(64) if i not in nonrouted_v2a_channels]
    cids = [12, 13, 14, 22, 23, 24, 32, 33, 34]
    
    
    markers = ['.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
    colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
    
    chip12 = df.loc[df['chip_id'] == 12]
    min_time = min(chip12['timestamp'])
    
    for i in range(len(cids)):
        chip = df.loc[df['chip_id'] == cids[i]]
        for ch in range(len(routed_v2a_channels)):
            channel = chip.loc[chip['channel_id']==routed_v2a_channels[ch]]
            time = [i for i in list(channel['timestamp'][:])]
            if len(time) != 0:
                for t in time:
                    t_chan = channel.loc[channel['timestamp'] == t]
                    adc = int(t_chan['dataword'][:])
                    ax[1].scatter(t-min_time, adc, color = colors[i], marker = markers[ch%15], s = 1)
                    
    
    data = list(df['dataword'])
    
    ax[0].grid(alpha = 0.5)
    ax[0].hist(data, bins = np.linspace(0, 250, 250), log = True, histtype = u'step')
    ax[0].set_xlabel('ADC')
    ax[0].set_ylabel('trigger count')
    
    ax[1].grid(alpha = 0.5)
    ax[1].set_xlabel('Time')
    ax[1].set_ylabel('ADC')
    
    
    plt.savefig('adc_trigger_all.png')
    
def plot_charge_all_trigger(filename):
    """
    Plots the charge trigger rate and Charge vs. Time for all channels on all chips

    Parameters
    ----------
    filename : str
        Name of file

    Returns
    -------
    None.

    """
    f = h5py.File(filename,'r')
    fig, ax = plt.subplots(2, 1, figsize = (8, 8))
    
    df = pd.DataFrame(f['packets'][:])
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]
    
    nonrouted_v2a_channels=[6,7,8,9,22,23,24,25,38,39,40,54,55,56,57]
    routed_v2a_channels=[i for i in range(64) if i not in nonrouted_v2a_channels]
    cids = [12, 13, 14, 22, 23, 24, 32, 33, 34]
    
    
    markers = ['.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
    colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
    
    chip12 = df.loc[df['chip_id'] == 12]
    min_time = min(chip12['timestamp'])
    
    for i in range(len(cids)):
        chip = df.loc[df['chip_id'] == cids[i]]
        for ch in range(len(routed_v2a_channels)):
            channel = chip.loc[chip['channel_id']==routed_v2a_channels[ch]]
            time = [i for i in list(channel['timestamp'][:])]
            if len(time) != 0:
                for t in time:
                    t_chan = channel.loc[channel['timestamp'] == t]
                    adc = int(t_chan['dataword'][:])
                    charge = ADC_to_charge(adc) 
                    ax[1].scatter(t-min_time, charge, color = colors[i], marker = markers[ch%15], s = 1)
                    
    
    data = [ADC_to_charge(a) for a in list(df['dataword'])]
    
    ax[0].grid(alpha = 0.5)
    ax[0].hist(data, bins = np.linspace(-250, 0, 250), log = True, histtype = u'step')
    ax[0].set_xlabel('Charge')
    ax[0].set_ylabel('trigger count')
    
    ax[1].grid(alpha = 0.5)
    ax[1].set_xlabel('Time')
    ax[1].set_ylabel('Charge')
    
    
    plt.savefig('charge_trigger_all.png')


def plot_selected_adc_trigger(filename, start_time, end_time):
    """
    Plots the ADC trigger rate and ADC vs. Time for all channels on all chips for a selected time period

    Parameters
    ----------
    filename : str
        Name of file
    start_time : float
        Start time for selection in seconds
    end_time : float
        End time for selection in seconds

    Returns
    -------
    None.

    """
    f = h5py.File(filename,'r')
    fig, ax = plt.subplots(2, 1, figsize = (8, 8))
    
    df = pd.DataFrame(f['packets'][:])
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]
    
    nonrouted_v2a_channels=[6,7,8,9,22,23,24,25,38,39,40,54,55,56,57]
    routed_v2a_channels=[i for i in range(64) if i not in nonrouted_v2a_channels]
    cids = [12, 13, 14, 22, 23, 24, 32, 33, 34]
    
    
    markers = ['.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
    colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
    
    chip12 = df.loc[df['chip_id'] == 12]
    min_time = min(chip12['timestamp'])
    
    data = []
    for i in range(len(cids)):
        chip = df.loc[df['chip_id'] == cids[i]]
        for ch in range(len(routed_v2a_channels)):
            channel = chip.loc[chip['channel_id']==routed_v2a_channels[ch]]
            time = [i for i in list(channel['timestamp'][:])]
        
            if len(time) != 0:
                for t in time:
                        if start_time*1e7 < t-min_time < end_time*1e7:
                            t_chan = channel.loc[channel['timestamp'] == t]
                            adc = int(t_chan['dataword'][:])
                            data.append(adc)
                            ax[1].scatter(t-min_time, adc, color = colors[i], marker = markers[ch%15], s = 1.2)
    
    ax[0].grid(alpha = 0.5)
    ax[0].hist(data, bins = np.linspace(0, 250, 250), log = True, histtype = u'step')
    ax[0].set_xlabel('ADC')
    ax[0].set_ylabel('trigger count')
    
    ax[1].grid(alpha = 0.5)
    ax[1].set_xlabel('Time')
    ax[1].set_ylabel('ADC')
    plt.show()
    
    plt.savefig('selected_adc_trigger.png')
    
    
def plot_selected_charge_trigger(filename, start_time, end_time):
    """
    Plots the charge trigger rate and Charge vs. Time for all channels on all chips for a selected time period

    Parameters
    ----------
    filename : str
        Name of file
    start_time : float
        Start time for selection in seconds
    end_time : float
        End time for selection in seconds

    Returns
    -------
    None.

    """
    f = h5py.File(filename,'r')
    fig, ax = plt.subplots(2, 1, figsize = (8, 8))
    
    df = pd.DataFrame(f['packets'][:])
    df = df.loc[df['packet_type'] == 0]
    df = df.loc[df['valid_parity'] == 1]
    
    nonrouted_v2a_channels=[6,7,8,9,22,23,24,25,38,39,40,54,55,56,57]
    routed_v2a_channels=[i for i in range(64) if i not in nonrouted_v2a_channels]
    cids = [12, 13, 14, 22, 23, 24, 32, 33, 34]
    
    
    markers = ['.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
    colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
    
    chip12 = df.loc[df['chip_id'] == 12]
    min_time = min(chip12['timestamp'])
    
    data = []
    for i in range(len(cids)):
        chip = df.loc[df['chip_id'] == cids[i]]
        for ch in range(len(routed_v2a_channels)):
            channel = chip.loc[chip['channel_id']==routed_v2a_channels[ch]]
            time = [i for i in list(channel['timestamp'][:])]
        
            if len(time) != 0:
                for t in time:
                        if start_time*1e7 < t-min_time < end_time*1e7:
                            t_chan = channel.loc[channel['timestamp'] == t]
                            adc = int(t_chan['dataword'][:])
                            charge = ADC_to_charge(adc)
                            data.append(charge)
                            ax[1].scatter(t-min_time, charge, color = colors[i], marker = markers[ch%15], s = 1.2)
    
    ax[0].grid(alpha = 0.5)
    ax[0].hist(data, bins = np.linspace(-250, 0, 250), log = True, histtype = u'step')
    ax[0].set_xlabel('Charge')
    ax[0].set_ylabel('trigger count')
    
    ax[1].grid(alpha = 0.5)
    ax[1].set_xlabel('Time')
    ax[1].set_ylabel('Charge')
    plt.show()
    
    plt.savefig('selected_charge_trigger.png')
