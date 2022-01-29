import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import sys


WIN_HOP_LENGTH = 512
N_FFT = 2048


def create_spectrogram(voice_record_path: str, save_path: str, mode='stft'):
    """Creates spectrogram of provided sound record in given mode of processing

    Args:
        voice_record_path (str): path to the sound records
        save_path (str): destination file path
        mode (str, optional): mode of creating the spectrogram - 'stft' -> Short-Time Fourier Transform, 'mel' -> Mel-Spectrogram. Defaults to 'stft'.
    """
    fig, ax = plt.subplots()
    ax.axis('off')

    some_sound, sampling_rate = librosa.load(voice_record_path)

    if mode == 'mel':
        img_array = librosa.feature.melspectrogram(
            y=some_sound,
            sr=sampling_rate,
            hop_length=WIN_HOP_LENGTH,
            win_length=WIN_HOP_LENGTH,
            n_mels=256)
        M_db = librosa.power_to_db(img_array, ref=np.max)
        img = librosa.display.specshow(M_db, y_axis='mel', x_axis='time')

    elif mode == 'stft':
        D = np.abs(librosa.stft(some_sound, n_fft=N_FFT,
                   hop_length=WIN_HOP_LENGTH))
        DB = librosa.amplitude_to_db(D, ref=np.max)
        librosa.display.specshow(
            DB, sr=sampling_rate, hop_length=WIN_HOP_LENGTH, x_axis='time', y_axis='log')
    fig.savefig(save_path, bbox_inches='tight', pad_inches=0)
    plt.figure().clear()
    plt.close()
    plt.cla()
    plt.clf()


def main():
    try:
        if '--help' in sys.argv:
            print("#  Use it THIS way:\n#  >> python record_to_image.py <record_path_with_extension> <new_image_name_with_extension> <mode>\n\n*mode regards the way of creating spectrogram \n\t- 'mel' for built in melspectrogram function\n\t- 'stft' for STFT (Fourier Transform)#")
            return
        record_name = sys.argv[1]
        new_file_name = sys.argv[2]
        mode = sys.argv[3].lower()
        print(f"{mode} ===> {record_name} -> {new_file_name}")
    except:
        print("Wrong input provided")
        return

    create_spectrogram(voice_record_path=record_name,
                       save_path=new_file_name,
                       mode=mode)



if __name__ == "__main__":
    main()
