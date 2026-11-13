# Originally written by Shriya Sudharshan, Modified by Hadrian Ward
# Not in working state, need to frequency-shift recording

import numpy as np
import matplotlib.pyplot as plt
from constants import *
import load_and_plot

def analyze(baseline_data):
	phase_diff = baseline_data[1:] * np.conj(baseline_data[:-1])
	baseline_freq = (SAMPLE_RATE/(2*np.pi))*np.angle(phase_diff)
	baseline_time = np.arange(len(baseline_freq)) / SAMPLE_RATE

	plt.figure(figsize=(10,4))
	plt.plot(baseline_time * 1000, baseline_freq / 1000)
	plt.xlabel("Time (ms)")
	plt.ylabel("Instantaneous Frequency (kHz)")
	plt.title(
		f"Baseline BLE Instantaneous Frequency\n"
		f"Center Frequency = {nominal_freq/1e6} MHz, "
		f"Sampling Rate = {SAMPLE_RATE/1e6} MS/s"
	)

	plt.grid()
	plt.show()

	for d in detuning_khz:

		rx_freq = nominal_freq + d*1000
		sdr.rx_lo = int(rx_freq)
		print("\n--------------------------------")
		print("Receiver Frequency =", rx_freq/1e6, "MHz")
		print("Detuning =", d, "kHz")
		sdr.rx()  # Discard first capture after changing frequency
		data = sdr.rx()  # Use this capture for analysis

		phase_diff = data[1:] * np.conj(data[:-1])
		freq = (SAMPLE_RATE/(2*np.pi))*np.angle(phase_diff)
		freq_khz = freq / 1000

		if d in example_detunings:

			saved_waveforms[d] = freq_khz.copy()
			time_axis = np.arange(len(freq_khz)) / SAMPLE_RATE
			saved_times[d] = time_axis * 1000

		plt.figure(figsize=(8,4))
		plt.hist(freq_khz, bins=100)

		plt.xlabel("Frequency (kHz)")
		plt.ylabel("Count")

		plt.title(
			f"Instantaneous Frequency Histogram\n"
			f"Detuning = {d} kHz"
		)

		plt.grid()
		plt.show()
		center = float(
			input(
				"Enter estimated center between the two GFSK peaks (kHz): "
			)
		)

		observed_center.append(center)

	print("\nResults")
	print("Detuning (kHz)    Center (kHz)")
	print("------------------------------")

	for d, c in zip(detuning_khz, observed_center):

		print(f"{d:8.0f} {c:18.2f}")

	plt.figure(figsize=(8,5))
	plt.plot(
		detuning_khz,
		observed_center,
		'o-',
		linewidth=2
	)

	plt.xlabel("Receiver Detuning (kHz)")
	plt.ylabel("Observed GFSK Center (kHz)")

	plt.title(
		"Observed GFSK Center vs Receiver Detuning"
	)

	plt.grid()
	plt.show()
	plt.figure(figsize=(10,8))

	plot_num = 1

	for d in example_detunings:

		plt.subplot(3,1,plot_num)
		plt.plot(
			saved_times[d],
			saved_waveforms[d],
			linewidth=1
		)

		plt.axhline(
			y=0,
			color='red',
			linestyle='--',
			label='0 kHz Threshold'
		)

		plt.title(
			f"Instantaneous Frequency\n"
			f"Detuning = {d} kHz"
		)

		plt.ylabel("Frequency (kHz)")
		plt.grid()
		plt.legend()

		plot_num += 1

	plt.xlabel("Time (ms)")
	plt.tight_layout()
	plt.show()

	print("\nPart C: Zero Threshold Analysis")

	for d in example_detunings:

		freq = saved_waveforms[d]

		above = np.sum(freq >= 0) / len(freq) * 100
		below = np.sum(freq < 0) / len(freq) * 100

		print("\nDetuning:", d, "kHz")
		print("Above zero:", round(above, 2), "%")
		print("Below zero:", round(below, 2), "%")

def main():
	data = load_and_plot.load_iq(FILE_NAME)
	analyze(data)

if __name__ == "__main__":
    main()