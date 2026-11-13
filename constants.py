SAMPLE_RATE = 8e6
RX_BUFFER_SIZE = 262144
RX_RF_BANDWIDTH = 2e6# No more then half sample rate because nyquist
RX_LO = 2.426e9
FILE_NAME = "ble_signal_save.csv"# Each line is: I,Q
DETECTION_WINDOW_SIZE_SAMPLES = 500# Average power for 10 samples to detect signal