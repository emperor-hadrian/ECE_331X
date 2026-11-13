# By Hadrian Ward
# Meant to find a BLE signal and save a recording which can be used for later tests
# A burst lasts about 300us (https://rfessentials.com/resources/rf-glossary/ble-advertising/)
# A recording of 262144 samples or 26.2144ms should be enough to spot BLE signals

import adi
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from math import *
from constants import *
import load_and_plot

SIGNAL_AVG_ABOVE_NOISE_DB = 30# How much above noise floor to be considered the start of a signal
SAVE_SAMPLE_MARGIN_BEFORE_AFTER = 500# Include noise before and after signal

def db(x):
    return 10*log(abs(x),10)

# DOES NOT DECODE: That is for another function
# Returns: Either `None` if nothing found or a tuple (start, end) of indices where the signal starts and ends
def detect_ble(data):
    # Slide a "window" over data to see if frequency is less then 500KHz
    lowest_avg_db = None
    signal_start_i = None
    signal_end_i = None
    currently_in_signal = False
    for start_i in range(0,len(data),DETECTION_WINDOW_SIZE_SAMPLES):
        # Get mean
        data_subset = data[start_i::start_i+DETECTION_WINDOW_SIZE_SAMPLES]
        avg_db = db(np.mean(data_subset))
        # Check lowest to determine noise floor
        if lowest_avg_db == None or avg_db < lowest_avg_db:
            lowest_avg_db = avg_db
        assert(lowest_avg_db != None)
        # Find start
        if avg_db >= lowest_avg_db + SIGNAL_AVG_ABOVE_NOISE_DB and not currently_in_signal:
            signal_start_i = start_i
            currently_in_signal = True
        # Find end
        if avg_db < lowest_avg_db + SIGNAL_AVG_ABOVE_NOISE_DB and currently_in_signal:
            signal_end_i = start_i
            currently_in_signal = False
            break
    if signal_start_i == None:
        return None
    else:
        if signal_end_i == None:
            return (signal_start_i, len(data))
        else:
            return (signal_start_i, signal_end_i)

def main():
    sdr = adi.Pluto("ip:192.168.2.1")
    sdr.sample_rate = SAMPLE_RATE
    sdr.rx_rf_bandwidth = int(RX_RF_BANDWIDTH)
    sdr.rx_buffer_size = RX_BUFFER_SIZE
    sdr.gain_control_mode = "slow_attack"
    sdr.rx_hardwaregain = 40
    sdr.rx_lo = int(RX_LO)
    print("SDR Setup")
    print("Looking for signals")
    data = None# Init these out of the loop so they remain in scope after loop ends
    result = None
    while True:
        data = sdr.rx()
        result = detect_ble(data)
        if result != None:
            break
    print("Signal found, saving")
    # Save
    start_index = max(0, result[0]-SAVE_SAMPLE_MARGIN_BEFORE_AFTER)
    end_index_exclusive = min(len(data), result[1]+SAVE_SAMPLE_MARGIN_BEFORE_AFTER)
    with open(FILE_NAME, "w") as f:
        f.write("")
        for i in range(start_index, end_index_exclusive):
            f.write(f"{str(data[i].real)},{str(data[i].imag)}\n")
    print(f"Signal recording at {SAMPLE_RATE} S/s with {end_index_exclusive-start_index} samples saved to {FILE_NAME}")
    # Plot
    load_and_plot.plot_mag_db(data[start_index:end_index_exclusive])

if __name__ == "__main__":
    main()