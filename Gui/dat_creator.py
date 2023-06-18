import numpy as np
import time
import pickle
from scipy.signal import butter, filtfilt

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Generate longer raw IQ data
sample_rate = 5e9  # 2.5 Msps
raw_iq_data = np.random.randn(int(1e5)) + 1j * np.random.randn(int(1e5))

# Set center frequency
center_frequency = 1.5e9  # 1.5 GHz

# Get the current timestamp
timestamp = time.time()

# Apply a low-pass and high-pass filter to simulate attenuation below 1350 MHz and above 1800 MHz
low_cutoff = 1350e6
high_cutoff = 1800e6
filtered_iq_data = highpass_filter(raw_iq_data, low_cutoff, sample_rate)
filtered_iq_data = lowpass_filter(filtered_iq_data, high_cutoff, sample_rate)

# Save the data to a file
data_dict = {
    'raw_iq_data': filtered_iq_data,
    'center_frequency': center_frequency,
    'sample_rate': sample_rate,
    'timestamp': timestamp
}

with open(r'C:\Users\Ethan\Desktop\test_data.dat', 'wb') as f:
    pickle.dump(data_dict, f)
