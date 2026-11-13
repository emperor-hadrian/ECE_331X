# Loads IQ file

from constants import *
import matplotlib.pyplot as plt
import numpy as np

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

def main():
    data = load_iq(FILE_NAME)
    plot_mag_db(data)

if __name__ == "__main__":
    main()