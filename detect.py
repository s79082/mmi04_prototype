import speech_recognition as sr

import tkinter as tk

import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import os

# Initialize the recognizer
recognizer = sr.Recognizer()

# Define the trigger word
TRIGGER_WORD = "stop"  # Replace with the word you want to use

def on_trigger_word_detected():
    """Action to take when the trigger word is detected."""
    print(f"The trigger word '{TRIGGER_WORD}' was detected!")

def listen_for_trigger(source):
    """Listen for speech and detect the trigger word."""
    try:
        # Adjust for ambient noise and capture audio
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for the trigger word...")
        audio = recognizer.listen(source)
        
        # Recognize speech using Google's recognizer
        detected_text = recognizer.recognize_google(audio)
        print(f"Detected speech: {detected_text}")
        
        # Check if the trigger word is in the detected text
        if TRIGGER_WORD.lower() in detected_text.lower():
            on_trigger_word_detected()
        else:
            print(f"Trigger word '{TRIGGER_WORD}' not found.")
    except sr.UnknownValueError:
        print("Could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results from the recognition service; {e}")

if __name__ == "__main__":
    try:
        # Open the microphone once
        with sr.Microphone() as source:
            print("Microphone ready. Press Ctrl+C to exit.")
            while True:
                listen_for_trigger(source)
    except KeyboardInterrupt:
        print("\nExiting program.")

class AudioPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Player")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Initialize pygame mixer
        pygame.mixer.init()

        # Variable to store the current audio file
        self.current_audio_file = None
        self.is_paused = False

        # Create UI components
        self.create_widgets()

    def create_widgets(self):
        # Title Label
        self.title_label = tk.Label(self.root, text="Audio Player", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Audio File Label
        self.file_label = tk.Label(self.root, text="No file loaded", font=("Helvetica", 12))
        self.file_label.pack(pady=10)

        # Control Buttons
        self.play_button = tk.Button(self.root, text="Play", command=self.play_audio, width=10)
        self.play_button.pack(pady=5)

        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_audio, width=10)
        self.pause_button.pack(pady=5)

        self.resume_button = tk.Button(self.root, text="Resume", command=self.resume_audio, width=10)
        self.resume_button.pack(pady=5)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_audio, width=10)
        self.stop_button.pack(pady=5)

        # Load Audio Button
        self.load_button = tk.Button(self.root, text="Load Audio File", command=self.load_audio, width=15)
        self.load_button.pack(pady=20)

    def load_audio(self):
        """Load an audio file."""
        file_path = filedialog.askopenfilename(
            title="Select an Audio File",
            filetypes=(("Audio Files", "*.mp3 *.wav"), ("All Files", "*.*"))
        )
        if file_path:
            self.current_audio_file = file_path
            self.file_label.config(text=f"Loaded: {os.path.basename(file_path)}")
        else:
            messagebox.showerror("Error", "No file selected")

    def play_audio(self):
        """Play the loaded audio file."""
        if not self.current_audio_file:
            messagebox.showerror("Error", "No audio file loaded")
            return

        if self.is_paused:  # If paused, unpause
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:  # Otherwise, load and play the file
            pygame.mixer.music.load(self.current_audio_file)
            pygame.mixer.music.play()
            self.file_label.config(text=f"Playing: {os.path.basename(self.current_audio_file)}")

    def pause_audio(self):
        """Pause the currently playing audio."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True
            self.file_label.config(text="Paused")

    def resume_audio(self):
        """Resume paused audio."""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.file_label.config(text=f"Playing: {os.path.basename(self.current_audio_file)}")

    def stop_audio(self):
        """Stop the audio playback."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.is_paused = False
            self.file_label.config(text="Stopped")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioPlayerApp(root)
    root.mainloop()



