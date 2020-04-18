import numpy as np
from struct import unpack
import pyaudio
import logging


class FFT:
    def __init__(self):
        self.num_rows = 44
        logging.basicConfig(level=logging.DEBUG)
        self.chunk_size = 1024  # Use a multiple of 8 (FFT will compute faster with a multiple of 8)
        py_audio = pyaudio.PyAudio()
        device_index = 0
        device_info = py_audio.get_device_info_by_index(device_index)
        logging.debug(f'Using device {device_index}: {device_info})')
        self.sampling_frequency = int(device_info['defaultSampleRate'])  # 44100 Hz
        self.channels = device_info['maxInputChannels']  # 1
        self.audio_stream = py_audio.open(format=pyaudio.paInt16, channels=self.channels, rate=self.sampling_frequency,
                                          input=True, input_device_index=device_index)

        self.frequency_bins = [(0, 156), (156, 313), (313, 625), (625, 1250), (1250, 2500), (2500, 5000), (5000, 10000),
                               (10000, 20000)]  # Lower and upper frequencies of each frequency bin

        self.max_value_transformed_fft_data = 40
        self.weighting = [2, 6, 8, 16, 16, 32, 32, 64]  # scaling factors of frequency bins. rule of thumb: double frequency -> half power

    # Return power array index corresponding to a particular frequency
    def get_power_array_index_of_frequency(self, frequency):
        return int(self.channels * self.chunk_size * frequency / self.sampling_frequency)

    def start(self, var):
        spectrum_levels = np.array([0, 0, 0, 0, 0, 0, 0, 0])
        while True:
            audio_data = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
            audio_data = unpack("%dh" % (len(audio_data) / 2), audio_data)
            audio_data = np.array(audio_data, dtype='h')
            # apply fft
            fft_data = np.fft.rfft(audio_data)
            # remove last element in array to make it the same size as the chunk
            fft_data = np.delete(fft_data, len(fft_data) - 1)
            # transform complex fft data to real data
            fft_data = np.abs(fft_data)
            # divide fft data into the frequency bins
            for i, frequency_bin in enumerate(self.frequency_bins):
                low_index = self.get_power_array_index_of_frequency(frequency_bin[0])
                high_index = self.get_power_array_index_of_frequency(frequency_bin[1])
                spectrum_levels[i] = np.mean(fft_data[low_index:high_index])
                # TODO: use bell curve instead of mean (Flori)

            # tidy up spectrum level values
            spectrum_levels = np.divide(np.multiply(spectrum_levels, self.weighting), 1000000)
            # TODO: 1e6 determined empirically
            spectrum_levels = np.interp(spectrum_levels, [0, self.max_value_transformed_fft_data],  [0, self.num_rows]) # TODO: max_value_transformed_fft_data was determined empirically
            spectrum_levels = spectrum_levels.astype(int)
            var.spec_levels = spectrum_levels.tolist()
