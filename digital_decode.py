# After `extract_bits.py` in the pipeline

import load_and_plot
from constants import *
import extract_bits

ADVERT_PREAMBLE = 0b10101010
ADVERT_ACCESS_ADDRESS = 0x8E89BED6

# Return: int
def bits_to_int(bits):
	sum = 0
	for (bit_i, bit) in enumerate(bits):
		if bit:
			sum += 1 << bit_i
	return sum

# https://www.rfwireless-world.com/terminology/ble-advertising-data-packet-formats
# https://academy.nordicsemi.com/courses/bluetooth-low-energy-fundamentals/lessons/lesson-2-bluetooth-le-advertising/topic/advertisement-packet/
# This is only expecting advertising packets and won't work on anything else
def decode_ble_packet(bits):
	# Step forward until next 5 bytes are equal to the preamble + access address
	parse_i = 0
	success = False
	while parse_i < len(bits) - 40:
		if bits_to_int(bits[parse_i:parse_i+8]) == ADVERT_PREAMBLE and bits_to_int(bits[parse_i+8:parse_i+40]) == ADVERT_ACCESS_ADDRESS:
			success = True
			break
		parse_i += 1
	parse_i += 40# Set to end of access address
	if not success:
		return None
	print("Found match for preamble + access address")
	# Next is the BLE Advertising channel PDU (protocal data unit)
	# Header: 16 bits, Payload: Length in bytes is specified in header
	pdu_type = bits_to_int(bits[parse_i:parse_i+4])
	payload_len = bits_to_int(bits[parse_i+8:parse_i+16])
	# TODO

def main():
	data = load_and_plot.load_iq(FILE_NAME)
	freq = load_and_plot.instantaneous_frequency(data, SAMPLE_RATE)
	(bits, bin_offset, samples_per_symbol) = extract_bits.extract_binary(freq, SAMPLE_RATE)
	decode_ble_packet(bits)

if __name__ == "__main__":
	main()