import adi
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


sdr = adi.Pluto(uri="ip:192.168.2.1")

sdr.sample_rate = int(4e6)
sdr.rx_lo = int(2426e6)  
sdr.rx_rf_bandwidth = int(4e6)
sdr.rx_buffer_size = 262144

sdr.gain_control_mode = "slow_attack"
sdr.rx_hardwaregain = 40

data = sdr.rx()

fs = sdr.sample_rate
N = len(data)

print("Samples acquired:", N)
print("Sampling rate:", fs)
print("Center frequency:", sdr.rx_lo)


magnitude = np.abs(data)

time = np.arange(N) / fs

plt.figure(figsize=(10, 4))
plt.plot(time * 1000, magnitude)
plt.xlabel("Time (ms)")
plt.ylabel("Magnitude")
plt.title("Received Signal Magnitude")
plt.grid()
plt.show()


phase = np.unwrap(np.angle(data))

plt.figure(figsize=(10, 4))
plt.plot(time, phase)
plt.xlabel("Time (s)")
plt.ylabel("Phase (radians)")
plt.title("Instantaneous Phase")
plt.grid()
plt.show()

freq = np.diff(phase) * (fs / (2 * np.pi))

freq_time = time[1:]

plt.figure(figsize=(10, 4))
plt.plot(freq_time * 1000, freq / 1000)
plt.xlabel("Time (ms)")
plt.ylabel("Frequency (kHz)")
plt.title("Instantaneous Frequency - Phase Difference")
plt.grid()
plt.show()


freq2angle = data[1:] * np.conj(data[:-1])

freq_2 = (fs / (2 * np.pi)) * np.angle(freq2angle)

plt.figure(figsize=(10, 4))
plt.plot(freq_time * 1000, freq_2 / 1000)
plt.xlabel("Time (ms)")
plt.ylabel("Frequency (kHz)")
plt.title("Instantaneous Frequency - IQ Method")
plt.grid()
plt.show()


plt.figure(figsize=(10, 4))
plt.hist(freq_2 / 1000, bins=150)
plt.xlabel("Frequency (kHz)")
plt.ylabel("Number of Samples")
plt.title("Instantaneous Frequency Distribution")
plt.grid()
plt.show()

