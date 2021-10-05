#imports
import numpy as np
import mne
from mne.preprocessing import ICA
from scipy import signal as signal
from time import perf_counter

from pyprep.find_noisy_channels import NoisyChannels

# subjectList = list of patients in subjects folder

#for subject in subjectList:

#load the EEG
rawEEG = mne.io.read_raw_cnt('demoeeg.cnt', preload=True)

rawEEGchannels = rawEEG.info['ch_names']

#remove extra channels BIP, EOG
rawEEG.pick_types(eeg=True,include=[], exclude=['EOG', 'BIP1', 'BIP2', 'BIP3', 'BIP4', 'BIP5', 'BIP6', 'BIP7', 'BIP8', 'BIP9', 'BIP10', 'BIP11', 'BIP12', 'BIP13', 'BIP14', 'BIP15', 'BIP16', 'BIP17', 'BIP18', 'BIP19', 'BIP20', 'BIP21', 'BIP22', 'BIP23', 'BIP24', 'BIP24_1'])

#set Montage
montage = mne.channels.make_standard_montage("standard_1020")
rawEEG.set_montage(montage, verbose=False)

#Crop first 15 seconds
rawEEG.crop(tmin=15)

#plot
print('plotting raw eeg ..')
#rawEEG.plot()

#bad channels (TODO: text SNR and other methods with EEG having flat channels and noisy channels)
print('Detecting bad channels ..')
nd = NoisyChannels(rawEEG)
start_time = perf_counter()
nd.find_bad_by_SNR()
print("--- %s seconds ---" % (perf_counter() - start_time))

print("bad channels are: ", nd.bad_by_SNR)    

rawEEG.info['bads'] = nd.bad_by_SNR

#save list of bad channels to a txt file in patient's folder

#Check number of bad channels or its ratio compared to total channels
#check if there is a certain number or ratio of bad channels to reject pt in literature

#plot before

#Interpolation?!
#interpEEG = rawEEG.copy().interpolate_bads(reset_bads=False) #If you want to reset bads list = True (which is default). Consider saving the bads to a txt file in the same folder to document that the script detected them and the current ones are interpolated.

#plot after to check if interpolated compared to before

#filter
print('filtering eeg ..')
filteredEEG = rawEEG.copy()
filteredEEG.filter(1, 35, picks='eeg', l_trans_bandwidth='auto', h_trans_bandwidth='auto',
            filter_length='auto', phase='zero', fir_window='hamming',
            fir_design='firwin')

#plot
print('plotting filtered eeg ..')
#filteredEEG.plot()

#rereferncing to common average
rereferencedEEG = filteredEEG.copy()
rereferencedEEG.set_eeg_reference(ref_channels='average')

#plot
print('plotting refernced eeg ..')
#rereferencedEEG.plot()

#save
rereferencedEEG.save("_referencedEEG.fif", overwrite=True) #saves in fif format

#Artifacts (ICA)
print('Running ICA ..')
ica = ICA(n_components=30, random_state=97, method='picard', max_iter=500)
ica.fit(rereferencedEEG)

ica.plot_sources(rereferencedEEG)
ica.plot_components()

#Artifact rejection

#save