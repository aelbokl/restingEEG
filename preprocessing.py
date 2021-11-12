#Resting EEG data preprocessing
#By Ahmed Elbokl. Special thanks to Dr. Mohammed Amr Sherif for his contribution.

#### THIS SCRIPT IS EXPECTED TO BE RUN THROUGH looper.py rather than running it directly ####

#TODO
#1. Add a log feature

#SETUP ---------------------------------------------------------------------------------------------------

#Raw EEG file extension
extension = '.cnt' #Supports '.cnt', '.fif'

#Filter parameters
l_freq = 1
h_freq = 35

#Plotting
plotting = True #Plotting is on by default. If you want to turn it off, set this to False. This will stop plotting altrhough the script except for the initial raw data, and ICA components plots.

#---------- DO NOT CHANGE CODE BELOW THAT LINE unless you know what you're doing ------------------------------

#imports
from matplotlib.pyplot import title
import numpy as np
import mne
import os
from mne.preprocessing import ICA
from scipy import signal as signal
from time import perf_counter

from pyprep.find_noisy_channels import NoisyChannels

#get list of all files in the current working directory with extension extension
files = [f for f in os.listdir() if f.endswith(extension)]

#if no files are found, throw an error
if len(files) == 0:
    raise Exception('No files found with extension ' + extension + ' in current working directory.')

#set data
filename = files[0]

#get filename without extension
filename_no_ext = filename.split('.')[0]

#load the EEG
if extension.lower() == '.cnt':
    rawEEG = mne.io.read_raw_cnt(filename, preload=True)
else:
    rawEEG = mne.io.read_raw_fif(filename, preload=True)

#get eeg channel names
rawEEGchannels = rawEEG.info['ch_names']

#remove extra channels BIP, EOG
rawEEG.pick_types(eeg=True,include=[], exclude=['EOG', 'BIP1', 'BIP2', 'BIP3', 'BIP4', 'BIP5', 'BIP6', 'BIP7', 'BIP8', 'BIP9', 'BIP10', 'BIP11', 'BIP12', 'BIP13', 'BIP14', 'BIP15', 'BIP16', 'BIP17', 'BIP18', 'BIP19', 'BIP20', 'BIP21', 'BIP22', 'BIP23', 'BIP24', 'BIP24_1'])

#set Montage
montage = mne.channels.make_standard_montage("standard_1020")
rawEEG.set_montage(montage, verbose=False)

#Crop first 15 seconds
rawEEG.crop(tmin=15)

#plot raw EEG for preview
print('plotting raw eeg .. Please check')
rawEEG.plot(n_channels=len(rawEEGchannels), block=True, title='Raw EEG')

#Ask user if he/she wants to continue after reviewing the EEG. If not, exit
ans = input('Do you wish to continue? (y/n)')
if ans == 'n':
    print('Exiting..')
    exit()  

#bad channels (TODO: text SNR and other methods with EEG having flat channels and noisy channels)
print('Detecting bad channels ..')
nd = NoisyChannels(rawEEG)
start_time = perf_counter()
nd.find_bad_by_SNR()
print("--- %s seconds ---" % (perf_counter() - start_time))

if len(nd.bad_by_SNR) > 0:
    print("bad channels are: ", nd.bad_by_SNR)
    rawEEG.info['bads'] = nd.bad_by_SNR

#save bad channels to a txt file for reference
with open('bad_channels.txt', 'w') as f:
    #if there are bad channels, write them to the file
    if len(nd.bad_by_SNR) > 0:
        for i in nd.bad_by_SNR:
            f.write(i + '\n')
    #if there are no bad channels, record that
    else:
        f.write('No bad channels found')

#Check number of bad channels or its ratio compared to total channels
#check if there is a certain number or ratio of bad channels to reject pt in literature

#Interpolation
print('Interpolating bad channels ..')
start_time = perf_counter()
interpolatedEEG = rawEEG.copy()
interpolatedEEG.interpolate_bads(reset_bads=True)
print("--- %s seconds ---" % (perf_counter() - start_time))

#plot after to check if interpolated compared to before
if plotting:
    print('plotting interpolated eeg .. Please check')
    interpolatedEEG.plot(n_channels=len(rawEEGchannels), title='Interpolated EEG')

#SAVE after adding suffix _interpolated to filename_no_ext
filename_no_ext = filename_no_ext + '_interpolated'
interpolatedEEG.save(filename_no_ext + '.fif', overwrite=True)

#filter
print('filtering eeg ..')
filteredEEG = rawEEG.copy()
filteredEEG.filter(l_freq, h_freq, picks='eeg', l_trans_bandwidth='auto', h_trans_bandwidth='auto',
            filter_length='auto', phase='zero', fir_window='hamming',
            fir_design='firwin')

#save after adding suffix _filtered to filename_no_ext
filename_no_ext = filename_no_ext + '_filtered'
filteredEEG.save(filename_no_ext + '.fif', overwrite=True)

#rereferencing to common average
rereferencedEEG = filteredEEG.copy()
rereferencedEEG.set_eeg_reference(ref_channels='average')

#SAVE after adding suffix _rereferenced to filename_no_ext
filename_no_ext = filename_no_ext + '_rereferenced'
rereferencedEEG.save(filename_no_ext + '.fif', overwrite=True) #saves in fif format

#Artifacts (ICA)
print('Running ICA ..')
icaEEG = rereferencedEEG.copy()
ica = ICA(n_components=30, random_state=97, method='picard', max_iter=500)
start_time = perf_counter()
ica.fit(icaEEG)
print("--- %s seconds ---" % (perf_counter() - start_time))

#plot sources
print('plotting ICA sources .. Please check to select which components to delete if any')
ica.plot_sources(icaEEG)

#plot components
ica.plot_components()

#Let user enter component numbers to be deleted
components_to_delete = input('Enter components to delete (separated by commas): ')
components_to_delete = components_to_delete.split(',')

#Delete components
ica.exclude = components_to_delete

#Remix ICA
icaEEG = ica.apply(icaEEG)

#save ICA with suffix _ica to filename_no_ext
filename_no_ext = filename_no_ext + '_ica'
icaEEG.save(filename_no_ext + '.fif', overwrite=True)

#Plot EEG after ICA remix
if plotting:
    print('plotting EEG after remixing ICA .. Please check')
    icaEEG.plot(n_channels=len(rawEEGchannels), block=True, title='EEG after ICA Remixing')

#Epoch the data into segments 1 seconds each
print('Epoching data ..')
events = mne.make_fixed_length_events(rereferencedEEG, duration=1)
epochs = mne.Epochs(rereferencedEEG, events, tmin=0, tmax=1, baseline=None, preload=True)

#Reject epochs with artifacts
rejections_criteria = dict(eeg=100e-6) #100 microV
epochs.drop_bad(reject=rejections_criteria) # see https://mne.tools/stable/generated/mne.Epochs.html to set reject parameters (based on peak-to-peak amplitude)

#plot
if plotting:
    epochs.plot(n_channels=len(rawEEGchannels), title='Epoched EEG')

#Save epochs after adding suffix _epoched to filename_no_ext
filename_no_ext = filename_no_ext + '_epoched'
epochs.save(filename_no_ext + '.fif', overwrite=True)
