import numpy as np
import time
import pickle

# Generate random raw IQ data
raw_iq_data = np.random.randn(1000) + 1j * np.random.randn(1000)

# Set center frequency and sample rate
center_frequency = 1.5e9  # 1.5 GHz
sample_rate = 2.5e6  # 2.5 Msps

# Get the current timestamp
timestamp = time.time()

# Save the data to a file
data_dict = {
    'raw_iq_data': raw_iq_data,
    'center_frequency': center_frequency,
    'sample_rate': sample_rate,
    'timestamp': timestamp
}

with open('test_data.dat', 'wb') as f:
    pickle.dump(data_dict, f)