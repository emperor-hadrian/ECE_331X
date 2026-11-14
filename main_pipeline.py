# Tests how far the frequency can be offset while still having the same bit reading as the original
# This program does not include actually recieving data,
# it assumes there is a pre-recorded signal stored with the name given by constants.FILE_NAME

from math import *
from constants import *
import extract_bits
import load_and_plot
import misc_analysis
import digital_decode

def example_detune_retune_using_iq(original_iq):
	original_freq = misc_analysis.instantaneous_frequency(original_iq, SAMPLE_RATE)
	load_and_plot.plot_freq(original_freq, "Original frequency before detune")
	# Detune
	detune = 100_000
	detuned_iq = misc_analysis.apply_freq_offset(original_iq, SAMPLE_RATE, detune)
	detuned_freq = misc_analysis.instantaneous_frequency(detuned_iq, SAMPLE_RATE)
	load_and_plot.plot_freq(detuned_freq, "Detuned by -100 KHz, IQ rotation")
	# Retune
	retuned_iq = misc_analysis.correct_freq_offset(detuned_iq, SAMPLE_RATE)
	retuned_freq = misc_analysis.instantaneous_frequency(retuned_iq, SAMPLE_RATE)
	load_and_plot.plot_freq(retuned_freq, "Retuned Freq, IQ rotation")

def example_detune_retune_using_freq_shift(original_iq):
	original_freq = misc_analysis.instantaneous_frequency(original_iq, SAMPLE_RATE)
	# Detune
	detune = 100_000
	detuned_freq = [x - detune for x in original_freq]
	load_and_plot.plot_freq(detuned_freq, "Detuned by -100 KHz, freq shift")
	# Retune
	avg = sum(detuned_freq) / len(detuned_freq)
	retuned_freq = [x - avg for x in detuned_freq]
	load_and_plot.plot_freq(retuned_freq, "Retuned Freq, freq shift")

def main():
	# Load test data
	original_iq_data = load_and_plot.load_iq(FILE_NAME)
	original_freq = misc_analysis.instantaneous_frequency(original_iq_data, SAMPLE_RATE)
	original_bits = extract_bits.extract_binary(original_freq, SAMPLE_RATE)[0]
	# Detune demo
	example_detune_retune_using_iq(original_iq_data)
	example_detune_retune_using_freq_shift(original_iq_data)
	# Test limits by finding offset limit in both directions
	# This does binary search
	limits = []# Lower bound, upper bound, in terms of local oscillator offset
	for sign in [-1, 1]:
		# Binary search for when it cannot be decoded anymore
		inner_bound = 0
		outer_bound = 8e6 * sign
		while True:
			halfway = (outer_bound + inner_bound) / 2
			# Detune
			detuned_iq = misc_analysis.apply_freq_offset(original_iq_data, SAMPLE_RATE, halfway)
			# Correct for offset
			retuned_iq = misc_analysis.correct_freq_offset(detuned_iq, SAMPLE_RATE)
			retuned_freq = misc_analysis.instantaneous_frequency(retuned_iq, SAMPLE_RATE)
			# Extract bits
			(retuned_bits, bin_offset, samples_per_symbol) = extract_bits.extract_binary(retuned_freq, SAMPLE_RATE)
			if digital_decode.decode_ble_packet(retuned_bits)[0] > 0:#retuned_bits == original_bits:
				# Highest offset that decodes correctly
				if abs(outer_bound - inner_bound) < 10000:# 10 KHz precision
					limits.append(halfway)
					extract_bits.plot_freq_with_bits(retuned_freq, retuned_bits, bin_offset, samples_per_symbol, title=f"Frequency With Decoded Bits, LO Offset limit = {halfway}Hz")
					break
				inner_bound = halfway
			else:
				outer_bound = halfway
	print(f"Lowest LO offset: {limits[0]}, Upper: {limits[1]}")

if __name__ == "__main__":
    main()