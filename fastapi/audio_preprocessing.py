from scipy import signal
from scipy.io import wavfile
import tempfile
from matplotlib import pyplot as plt

def audio_to_melspectrogram(audio_file):
    sample_rate, samples = wavfile.read(audio_file)
    samples_mono = samples.mean(axis=1)
    frequencies, times, spectrogram = signal.spectrogram(samples_mono, sample_rate)
    plt.pcolormesh(times, frequencies, spectrogram)
    test = tempfile.SpooledTemporaryFile()
    plt.savefig(test)
    test.seek(0)
    return test