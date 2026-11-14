from constants import *
import numpy as np
from math import *

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

# Applyes frequency shift, note that positive `offset` will result in the IQ data being frequency shifted negative
# Given: Complex IQ pairs
# Returns: Complex IQ pairs
def apply_freq_offset(original_data, sample_rate, offset_freq):
	out = []
	for (i, original_iq) in enumerate(original_data):
		mag = abs(original_iq)
		if mag == 0:
			out.append(0)
		else:
			angle = atan2(original_iq.imag, original_iq.real)
			angle -= offset_freq * 2 * pi * i / sample_rate
			out.append(mag * (cos(angle) + 1j*sin(angle)))
	return out

# Given: Complex IQ pairs
# Returns: Complex IQ pairs
def correct_freq_offset(original_data, sample_rate):
	freq = instantaneous_frequency(original_data, sample_rate)
	offset = sum(freq) / len(freq)
	return apply_freq_offset(original_data, sample_rate, offset)
