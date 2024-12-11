import os
import pygame
import struct
import time
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import speech_recognition as sr
import threading


class AudioPlayer:
    def __init__(self):
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

        # Audio playback state
        self.is_paused = False
        self.is_playing = False
        self.current_audio_file = None

        # PyAudio parameters
        self.p = pyaudio.PyAudio()
        self.chunk_size = 1024  # Size of each audio chunk
        self.rate = 44100  # Sampling rate for audio
        self.stream = None
        self.is_streaming = False

        # Speech recognition setup
        self.recognizer = sr.Recognizer()

        # Noise detection setup
        self.noise_threshold = 2000  # Adjust for loud noises like finger snaps
        self.noise_duration = 0.2  # Duration for detecting loud noises
        self.last_noise_time = 0  # Time of last noise

    def start_audio_stream(self):
        """Start the audio stream for waveform capture."""
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk_size)
        self.is_streaming = True

    def stop_audio_stream(self):
        """Stop the audio stream."""
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.is_streaming = False

    def update_waveform(self, line, ax, y):
        """Update the waveform in real-time."""
        if self.is_streaming:
            audio_data = self.stream.read(self.chunk_size)
            audio_samples = np.array(struct.unpack("<" + "h" * (len(audio_data) // 2), audio_data), dtype=np.int16)
            
            # Update the plot with the new audio data
            ax.set_ydata(audio_samples)
            ax.relim()  # Recalculate limits
            ax.autoscale_view(True, True, True)  # Autoscale the view

    def play_audio(self):
        """Play the selected audio file."""
        if not self.current_audio_file:
            print("No audio file loaded.")
            return

        pygame.mixer.music.load(self.current_audio_file)
        pygame.mixer.music.play()
        self.is_playing = True
        self.start_audio_stream()

    def pause_audio(self):
        """Pause the audio playback."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True

    def resume_audio(self):
        """Resume the audio playback."""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def stop_audio(self):
        """Stop the audio playback."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.stop_audio_stream()
            self.is_playing = False
            self.is_paused = False

    def load_audio_file(self, file_path):
        """Load an audio file for playback."""
        self.current_audio_file = file_path

    def recognize_speech(self):
        """Run speech recognition in the background."""
        with sr.Microphone() as source:
            print("Speech recognition started. Say 'play', 'pause', 'stop', or 'resume'.")
            self.recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    print("Listening for command...")
                    audio = self.recognizer.listen(source)
                    command = self.recognizer.recognize_google(audio).lower()
                    print(f"Recognized command: {command}")

                    if "play" in command:
                        self.play_audio()
                    elif "pause" in command:
                        self.pause_audio()
                    elif "resume" in command:
                        self.resume_audio()
                    elif "stop" in command:
                        self.stop_audio()
                    else:
                        print("Unknown command.")
                except sr.UnknownValueError:
                    print("Could not understand the audio.")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")

    def start_speech_recognition_thread(self):
        """Start the speech recognition in a separate thread."""
        threading.Thread(target=self.recognize_speech, daemon=True).start()

    def run(self, audio_file_path):
        """Main method to run the audio player and start speech recognition."""
        self.load_audio_file(audio_file_path)

        # Create a figure for the waveform plot
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.set_xlim(0, self.chunk_size)
        ax.set_ylim(-30000, 30000)
        ax.set_title("Real-time Audio Waveform")

        # Create a line object to represent the waveform
        line, = ax.plot([], [], lw=2)

        # Set up the animation
        ani = FuncAnimation(fig, self.update_waveform, fargs=(line, ax), interval=20)

        # Start speech recognition thread
        self.start_speech_recognition_thread()

        # Show the plot
        plt.show()


if __name__ == "__main__":
    audio_player = AudioPlayer()
    audio_file_path = "C:\\Users\\morit\\Downloads\\StockTune-Aero Groove_1732717128.mp3"
    if os.path.exists(audio_file_path):
        audio_player.run(audio_file_path)
    else:
        print(f"Audio file {audio_file_path} does not exist.")
