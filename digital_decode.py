# After `extract_bits.py` in the pipeline
# Pretty good document: https://www.bluetooth.com/wp-content/uploads/2022/05/the-bluetooth-le-primer-v1.2.0.pdf

import load_and_plot
from constants import *
import extract_bits
import misc_analysis

ADVERT_PREAMBLE = 0b10101010
ADVERT_ACCESS_ADDRESS = 0x8E89BED6
# Copied from https://tyromancy.art/misc/sdr-mod2/
PDU_TYPES = {0: "ADV_IND", 1: "ADV_DIRECT_IND", 2: "ADV_NONCONN_IND", 3: "SCAN_REQ/AUX_SCAN_REQ",
	4: "SCAN_RSP", 5: "CONNECT_IND/AUX_CONNECT_REQ", 6: "ADV_SCAN_IND"}

# Return: int
def bits_to_int(bits):
	sum = 0
	for (bit_i, bit) in enumerate(bits):
		if bit:
			sum += 1 << bit_i
	return sum

# https://github.com/tapeout/ble-baseband/blob/master/doc/whitening.md
# https://www.rfwireless-world.com/articles/bluetooth-physical-layer-header-data-payload-processing
class WhiteningFilter:
	def __init__(self, channel_i: int):
		self.n = 1 + sum([(((channel_i >> (5-n)) & 1) << (n+1)) for n in range(6)])
	def process_bits(self, bits):
		out = []
		for bit in bits:
			bit_intified = int(bit) & 1
			out.append((bit_intified ^ ((self.n >> 6) & 1)) == 1)
			self.shift()
		return out
	def shift(self):
		old_bit_6 = (self.n >> 6) & 1
		self.n = self.n << 1
		# Set LSB
		self.n += old_bit_6
		# Set bit 4 (XOR with old_bit_6)
		new_bit_4 = ((self.n >> 4) & 1) ^ old_bit_6
		self.n = (self.n & 0b1101111) | (new_bit_4 << 4)

# To test, see table 4.1 at https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/low-energy-controller/sample-data.html
def test_whitener(channel_i):
	w = WhiteningFilter(channel_i)
	bits = [int(b) for b in w.process_bits([False] * 64)]
	return " ".join(["".join([str(b) for b in bits[i*8:i*8+8]]) for i in range(8)])

# https://academy.nordicsemi.com/courses/bluetooth-low-energy-fundamentals/lessons/lesson-2-bluetooth-le-advertising/topic/advertisement-packet/
# Returns: (length in bits, success, type, data)
def decode_advertisement_data_structure(bits):
	parse_i = 0
	if 16 > len(bits):# Need room for length and type
		return (16, False, None, None)
	ad_length = bits_to_int(bits[0:8])
	# TODO
	return (16, False, None, None)

def decode_advertisement_pdu_payload(bits, pdu_type: int):
	out = {}
	parse_i = 0
	if 48 > len(bits):
		return out
	out["bt_address"] = bits_to_int(bits[0:48])
	parse_i = 48
	# AdvData
	if pdu_type == 1:# ADV_DIRECT_IND
		return out
	advertisement_data_structures = []# (type, data)
	while parse_i < len(bits):
		(length_bits, success, ad_type, ad_data) = decode_advertisement_data_structure(bits[parse_i:])
		if not success:
			break
		advertisement_data_structures.append((ad_type, ad_data))
		parse_i += length_bits
	out["advertisement_data_structures"] = advertisement_data_structures
	return out

# https://www.rfwireless-world.com/terminology/ble-advertising-data-packet-formats
# https://academy.nordicsemi.com/courses/bluetooth-low-energy-fundamentals/lessons/lesson-2-bluetooth-le-advertising/topic/advertisement-packet/
# This is only expecting advertising packets and won't work on anything else
# Returns: (Progress code, {"possible": other info})
#   Progress code:
#     0 - Did not find preamble + access address
#     1 - Found preamble + access address
#     2 - Enough bits for PDU Header
#     3 - Enough bits for PDU Payload
#     4 - Enough bits for CRC
def decode_ble_packet(bits, channel_i):
	progress_code = 0
	extra_info = {}
	# Step forward until next 5 bytes are equal to the preamble + access address
	parse_i = 0
	success = False
	while parse_i < len(bits) - 40:
		if bits_to_int(bits[parse_i:parse_i+8]) == ADVERT_PREAMBLE and bits_to_int(bits[parse_i+8:parse_i+40]) == ADVERT_ACCESS_ADDRESS:
			success = True
			break
		parse_i += 1
	if not success:
		return (progress_code, extra_info)
	extra_info["preamble_start_bit_i"] = parse_i
	parse_i += 40# Set to end of access address
	progress_code = 1
	#print("Found match for preamble + access address")
	# Next is the BLE Advertising channel PDU (protocal data unit)
	# Whitening is applied to the entire PDU. The CRC is not part of the PDU so it is not whitened
	# Header: 16 bits, Payload: Length in bytes is specified in header
	whitener = WhiteningFilter(channel_i)
	pdu_header_end_i = parse_i+16
	if pdu_header_end_i > len(bits):
		return (progress_code, extra_info)
	progress_code = 2
	pdu_header = whitener.process_bits(bits[parse_i:pdu_header_end_i])
	pdu_type = bits_to_int(pdu_header[0:4])
	extra_info["pdu_type"] = pdu_type
	if pdu_type in PDU_TYPES:
		extra_info["pdu_type_str"] = PDU_TYPES[pdu_type]
	payload_len = bits_to_int(pdu_header[8:16])
	extra_info["payload_len_bytes"] = payload_len
	#print(f"Payload len: {payload_len}")
	parse_i = pdu_header_end_i
	# PDU Payload
	payload_end_i = parse_i+(payload_len*8)
	if payload_end_i > len(bits):
		return (progress_code, extra_info)
	progress_code = 3
	payload = whitener.process_bits(bits[parse_i:payload_end_i])
	extra_info |= decode_advertisement_pdu_payload(payload, pdu_type)
	parse_i = payload_end_i
	# CRC (Checksum)
	crc_end_i = parse_i+24
	if crc_end_i > len(bits):
		return (progress_code, extra_info)
	progress_code = 4
	crc = bits[parse_i:crc_end_i]

	# Done
	return (progress_code, extra_info)

def main():
	data = load_and_plot.load_iq(FILE_NAME)
	freq = misc_analysis.instantaneous_frequency(data, SAMPLE_RATE)
	(bits, bin_offset, samples_per_symbol) = extract_bits.extract_binary(freq, SAMPLE_RATE)
	print(f"Packet decode result: {str(decode_ble_packet(bits, CHANNEL_INDEX))}")

if __name__ == "__main__":
	main()