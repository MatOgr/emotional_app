from typing import List
import wave
import pyaudio
from model import GenerateReportRequest, Metadata
import logging
from awsutils import upload_file
from record_to_image import create_spectrogram

SAMPLE_LENGTH = 4  # Voice sample length in seconds


def save_audio_to_file(data: List, filename: str, audio: pyaudio):
    file = wave.open(filename, 'wb')

    sample_width = 4
    file.setsampwidth(sample_width)
    file.setnchannels(2)
    file.setframerate(44100)
    file.writeframes(b''.join(data))
    file.close()


def record_voice(metadata: Metadata, filename: str) -> str:
    audio = pyaudio.PyAudio()
    audio_stream = audio.open(format=pyaudio.paInt32,
                              rate=44100,
                              channels=2,
                              frames_per_buffer=1024,
                              input=True)

    data = []
    for i in range(int(44100 / 1024 * SAMPLE_LENGTH)):
        data.append(audio_stream.read(1024, exception_on_overflow=False))

    audio_stream.stop_stream()
    audio_stream.close()
    save_audio_to_file(data, filename, audio)
    audio.terminate()

def process_voice(metadata: Metadata, request: GenerateReportRequest):
    logging.info("Recording voice...")

    VOICE_FILENAME = "/api/voice/voice_" + metadata.recordID + ".wav"
    # Record voice and store in memory
    record_voice(metadata, VOICE_FILENAME)
    # Convert voice to image
    create_spectrogram(VOICE_FILENAME, VOICE_FILENAME[:-4])
    # Upload voice to S3
    upload_file(VOICE_FILENAME, VOICE_FILENAME, request)
