import sounddevice as sd
import numpy as np
import sys

# Set the sample rate and duration
sample_rate = 44100  # Sample rate in Hz (samples per second)
duration = 1  # Duration of the audio in seconds

# Function to calculate the volume (RMS value)
def get_audio_volume(indata):
    # Calculate the Root Mean Square (RMS) of the audio data
    volume_norm = np.linalg.norm(indata) * 10
    return volume_norm

# Callback function to get audio data in real time
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    volume = get_audio_volume(indata)
    print(f"Current volume: {volume:.2f}")

# Open an input stream and listen to the microphone
with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate):
    print("Press Ctrl+C to stop")
    try:
        while True:
            pass  # Just let the callback function handle everything
    except KeyboardInterrupt:
        print("Recording stopped.")
