# After `extract_bits.py` in the pipeline

import load_and_plot
from constants import *
import extract_bits
import misc_analysis

ADVERT_PREAMBLE = 0b10101010
ADVERT_ACCESS_ADDRESS = 0x8E89BED6

# Return: int
def bits_to_int(bits):
	sum = 0
	for (bit_i, bit) in enumerate(bits):
		if bit:
			sum += 1 << bit_i
	return sum

# https://www.allaboutcircuits.com/technical-articles/whitening-filters-help-low-power-radios-tackle-issues-caused-by-long-identical-bit-sequences/
def whitening_shift_reg(n) -> int:
	return 0# TODO

# https://www.rfwireless-world.com/terminology/ble-advertising-data-packet-formats
# https://academy.nordicsemi.com/courses/bluetooth-low-energy-fundamentals/lessons/lesson-2-bluetooth-le-advertising/topic/advertisement-packet/
# This is only expecting advertising packets and won't work on anything else
# Returns: (Progress code, possible other info, ...)
#   Progress code:
#     0 - Did not find preamble
#     1 - Found preamble + access address
#     2+- Not implemented
def decode_ble_packet(bits):
	progress_code = 0
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
		return (progress_code, None)
	progress_code = 1
	#print("Found match for preamble + access address")
	# Next is the BLE Advertising channel PDU (protocal data unit)
	# Header: 16 bits, Payload: Length in bytes is specified in header
	pdu_header_end_i = parse_i+16
	if pdu_header_end_i > len(bits):
		return (progress_code, None)
	pdu_header = bits[parse_i:pdu_header_end_i]
	pdu_type = bits_to_int(pdu_header[0:4])
	payload_len = bits_to_int(pdu_header[8:16])
	#print(f"Payload len: {payload_len}")
	parse_i += 16
	# Payload
	payload_end_i = parse_i+(payload_len*8)
	if payload_end_i + 24 > len(bits):
		return (progress_code, None)
	payload = bits[parse_i:payload_end_i]
	# Checksum
	# TODO
	# Done
	return (progress_code, None)# TODO

def main():
	data = load_and_plot.load_iq(FILE_NAME)
	freq = misc_analysis.instantaneous_frequency(data, SAMPLE_RATE)
	(bits, bin_offset, samples_per_symbol) = extract_bits.extract_binary(freq, SAMPLE_RATE)
	print(f"Packet decode result: {str(decode_ble_packet(bits))}")

if __name__ == "__main__":
	main()