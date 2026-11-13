# Extract 1s and 0s from GFSK signal

from constants import *
from math import *
import load_and_plot
import numpy as np
import matplotlib.pyplot as plt

# Detects 1 or 0 based on if frequency is >0 or <0
# Returns: (Avg abs avg per bin, List(bool for each bit))
def data_and_score_with_bin_offset(inst_freq, bin_offset, samples_per_symbol, n_bins):
	current_score = 0.0# For the current bin-offset
	bits = []
	for bin_i in range(n_bins):
		# Average inst freq across bin, add the absolute value of that to the current bin-offset score
		start_i = bin_offset + bin_i*samples_per_symbol
		end_i = start_i + samples_per_symbol
		inst_freq_bin_sum = 0.0
		for i in range(start_i, end_i):
			inst_freq_bin_sum += float(inst_freq[i])
		current_score += abs(inst_freq_bin_sum) / float(samples_per_symbol)
		bits.append(inst_freq_bin_sum > 0)
	return (current_score / float(n_bins), bits)

# Assumes BLE encoding of 1 symbol/bit per us
# Params: `inst_freq`: Array of calculated instantaneous frequencies, `sample_rate`: Sample rate
# Returns: list of scores for each symbol offset, starting at 0, until samples_per_symbol-1
# How it works: Puts every sample into 1us "bins". Sum absolute values of each bin's average,
# this is a score to figure out how well the bins are aligned with the signal's symbols.
# Repeat above process many times, each time incrementing the "bin offset" by 1 sample.
# There should be a good number of samples per symbol (like 8) for this to be accurate.
def find_bin_offset_scores(inst_freq, samples_per_symbol, n_bins):
	bin_offset_scores = []# Avg of each bin's abs avg, for each bin offset, len=samples_per_symbol
	# For each bin offset
	for bin_offset in range(samples_per_symbol):
		bin_offset_scores.append(data_and_score_with_bin_offset(inst_freq, bin_offset, samples_per_symbol, n_bins)[0])
	return bin_offset_scores

# Assumes BLE encoding of 1 symbol/bit per us
# Params: `inst_freq`: Array of calculated instantaneous frequencies, `sample_rate`: Sample rate
# Returns: (List(bool), bin offset, samples per symbol)
def extract_binary(inst_freq, sample_rate):
	samples_per_symbol = int(sample_rate/1e6)
	n_bins = int(len(inst_freq) / samples_per_symbol) - 1
	bin_offset_scores = find_bin_offset_scores(inst_freq, samples_per_symbol, n_bins)
	#print(f"Bin offset scores: {str(bin_offset_scores)}\n")
	# Now have `bin_offset_scores`, find which one is the highest
	max_score = max(bin_offset_scores)
	optimal_bin_offset = bin_offset_scores.index(max_score)
	# Get binary
	bits = data_and_score_with_bin_offset(inst_freq, optimal_bin_offset, samples_per_symbol, n_bins)[1]
	return (bits, optimal_bin_offset, samples_per_symbol)

def plot_freq_with_bits(inst_freq, bits, bin_offset, samples_per_symbol):
	time_array = np.arange(len(inst_freq)) * 1e6 / SAMPLE_RATE
	plt.figure(figsize=(10, 4))
	plt.plot(time_array, inst_freq)
	plt.xlabel("Time (us)")
	plt.ylabel("Inst. Freq. (Hz)")
	plt.title("Received Signal Frequency With Decoded Bits")
	# Background colors for bits, https://stackoverflow.com/questions/9957637
	bit_time = 1# Scale is in us
	for (bin_i, bit) in enumerate(bits):
		if bit:
			start_time = (bin_offset + (bin_i * samples_per_symbol)) * 1e6 / SAMPLE_RATE
			plt.axvspan(start_time, start_time+bit_time, facecolor='0.2', alpha=0.3)
	plt.grid()
	plt.show()

def main():
	data = load_and_plot.load_iq(FILE_NAME)
	freq = load_and_plot.instantaneous_frequency(data, SAMPLE_RATE)
	(bits, bin_offset, samples_per_symbol) = extract_binary(freq, SAMPLE_RATE)
	plot_freq_with_bits(freq, bits, bin_offset, samples_per_symbol)

if __name__ == "__main__":
	main()