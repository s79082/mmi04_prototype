import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import os
import threading
import speech_recognition as sr
import numpy as np  
import struct
from word2number import w2n  # Import word to number conversion

class AudioPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Player with Speech Control")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Initialize pygame mixer
        pygame.mixer.init()

        # Variable to store the current audio file
        self.current_audio_file = None
        self.is_paused = False

        # Create UI components
        self.create_widgets()

        # Start the speech recognition thread
        self.start_speech_recognition()

        self.volume = 1.0  # Initial volume is set to full (1.0)
        pygame.mixer.music.set_volume(self.volume)

    def create_widgets(self):
        # Title Label
        self.title_label = tk.Label(self.root, text="Audio Player", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Audio File Label
        self.file_label = tk.Label(self.root, text="No file loaded", font=("Helvetica", 12))
        self.file_label.pack(pady=10)

        # Control Buttons
        self.play_button = tk.Button(self.root, text="Play", command=self.play_audio, width=10)
        self.play_button.pack(side="left", padx=5)

        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_audio, width=10)
        self.pause_button.pack(side="left", padx=5)

        self.resume_button = tk.Button(self.root, text="Resume", command=self.resume_audio, width=10)
        self.resume_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_audio, width=10)
        self.stop_button.pack(side="left", padx=5)

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

    def highlight_button(self, button):
        """Highlight a button for 2 seconds."""
        original_color = button.cget("bg")
        button.config(bg="yellow")
        self.root.after(2000, lambda: button.config(bg=original_color))

    def start_speech_recognition(self):
        """Start the speech recognition in a separate thread."""
        threading.Thread(target=self.speech_recognition_thread, daemon=True).start()

    def calculate_rms(self, audio_data):
        """Calculate RMS (Root Mean Square) energy of the audio data."""
        # Convert the binary audio data into an array of signed 16-bit integers
        audio_samples = np.array(struct.unpack("<" + "h" * (len(audio_data) // 2), audio_data), dtype=np.int16)

        # Calculate RMS (Root Mean Square)
        rms = np.sqrt(np.mean(np.square(audio_samples)))
        return rms
    
    def lower_volume(self, command):
        """Lower the volume based on the command."""
        # Try to parse the number from the command
        try:
            if "to" in command:
                # Example: "lower volume to 8"
                volume_str = command.split("to")[1].strip()
                if len(volume_str) > 1:
                    if volume_str == "five":
                        new_volume = 0.5
                        
                else:
                    new_volume = float(volume_str)
                print(new_volume)
                if 0.0 <= new_volume <= 1.0:
                    self.volume = new_volume
                    pygame.mixer.music.set_volume(self.volume)
                    print(f"Volume set to {self.volume:.1f}")
                else:
                    print("Volume must be between 0 and 1.")
            elif "by" in command:
                # Example: "lower volume by two"
                volume_str = command.split("by")[1].strip()
                volume_decrease = w2n.word_to_num(volume_str)  # Convert word to number
                if volume_decrease > 0:
                    self.volume = max(0.0, self.volume - volume_decrease * 0.1)  # Decrease volume by 10% for each unit
                    pygame.mixer.music.set_volume(self.volume)
                    print(f"Volume decreased to {self.volume:.1f}")
                else:
                    print("Invalid volume decrease amount.")
        except ValueError:
            print("Could not parse the number from the command.")
        except Exception as e:
            print(f"Error in adjusting volume: {e}")

    def speech_recognition_thread(self):
        """Thread function for speech recognition."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Speech recognition started. Say 'play', 'pause', 'resume', or 'stop' to control the player.")
            recognizer.adjust_for_ambient_noise(source)
            while True:
                try:



                    print("Listening...")

                    
                    audio = recognizer.listen(source)                        
    

                    command = recognizer.recognize_google(audio).lower()
                    print(f"Recognized command: {command}")

                    if "play" in command:
                        self.highlight_button(self.play_button)
                        self.play_audio()
                    elif "pause" in command:
                        self.highlight_button(self.pause_button)
                        self.pause_audio()
                    elif "resume" in command:
                        self.highlight_button(self.resume_button)
                        self.resume_audio()
                    elif "stop" in command:
                        self.highlight_button(self.stop_button)
                        self.stop_audio()
                    elif "quieter" in command or "lower volume" in command:

                        self.lower_volume(command)
                    else:
                        print("Unknown command.")
                except sr.UnknownValueError:
                    print("Could not understand the audio.")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioPlayerApp(root)
    root.mainloop()
