# Loads IQ file

from constants import *
import matplotlib.pyplot as plt
import numpy as np
from math import atan2, pi

def load_iq(file_name):
	data = []
	with open(file_name, "r") as f:
		for line in f:
			if len(line) > 1:
				iq = line.split(",")
				data.append(float(iq[0]) + (1j*float(iq[1])))
	return data

def plot_mag_db(data):
	time_array = np.arange(len(data)) * 1e6 / SAMPLE_RATE
	plt.figure(figsize=(10, 4))
	plt.plot(time_array, 10*np.log10(np.abs(data)))
	plt.xlabel("Time (us)")
	plt.ylabel("Magnitude (dB)")
	plt.title("Received Signal Magnitude")
	plt.grid()
	plt.show()

# Uses phase difference between each sample
def instantaneous_frequency(data, sample_rate):
	output = [0]
	for i in range(1,len(data)):
		iq0 = data[i-1]
		iq1 = data[i]
		phase0=atan2(iq0.imag, iq0.real)
		phase1=atan2(iq1.imag, iq1.real)
		phase_diff = phase1 - phase0
		# Check if it crossed the -180 degree boundary
		if abs(phase_diff) > pi:
			if phase_diff > 0:
				phase_diff -= 2*pi
			else:
				phase_diff += 2*pi
		freq = (phase_diff / (2*pi)) * sample_rate
		output.append(freq)
	return output

def plot_freq(data):
	time_array = np.arange(len(data)) * 1e6 / SAMPLE_RATE
	plt.figure(figsize=(10, 4))
	plt.plot(time_array, data)
	plt.xlabel("Time (us)")
	plt.ylabel("Inst. Freq. (Hz)")
	plt.title("Received Signal Frequency")
	plt.grid()
	plt.show()

def main():
	data = load_iq(FILE_NAME)
	plot_mag_db(data)
	freq = instantaneous_frequency(data, SAMPLE_RATE)
	plot_freq(freq)

if __name__ == "__main__":
	main()