from pathlib import Path
import threading
from tkinter import Tk, Label, StringVar, Button, PhotoImage, Scale, Listbox
from pygame import mixer

import speech_recognition as sr

class MediaPlayer:
    def __init__(self, root):
        # Initialization
        mixer.init()
        self.current_volume = 0.5
        self.paused = False
        self.current_song_index = 0
        self.song_list = self.load_song_list()

        # Create main window
        self.window = root
        self.window.geometry("700x500")
        self.window.configure(bg="#5C5C68")
        self.window.resizable(False, False)

        # Variables
        self.current_song_var = StringVar()
        self.current_song_var.set("Not playing")

        # Class members for UI elements
        self.song_label = None
        self.volume_slider = None
        self.song_listbox = None
        self.buttons = {}

        self.setup_ui()
        #self.window.mainloop()

    def load_song_list(self):
        OUTPUT_PATH = Path(__file__).parent
        SONGS_PATH = OUTPUT_PATH / "songs"
        return [
            str(SONGS_PATH / "flow-211881.mp3"),
            str(SONGS_PATH / "amalgam-217007.mp3"),
            str(SONGS_PATH / "in-slow-motion-inspiring-ambient-lounge-219592.mp3"),
            str(SONGS_PATH / "nightfall-future-bass-music-228100.mp3"),
            str(SONGS_PATH / "perfect-beauty-191271.mp3")
        ]

    def setup_ui(self):
        # Song Label
        self.song_label = Label(
            self.window,
            textvariable=self.current_song_var,
            font=("Open Sans", 16),
            fg="white",
            bg="#19191D"
        )
        self.song_label.place(x=50, y=20)

        # Volume Slider
        self.volume_slider = Scale(
            self.window,
            from_=0,
            to=100,
            orient="vertical",
            length=250,
            bg="#ADADBB",
            troughcolor="#FFFFFF",
            command=self.update_volume
        )
        self.volume_slider.set(self.current_volume * 100)
        self.volume_slider.place(x=50, y=50)

        # Buttons
        self.create_buttons()

        # Song Listbox
        self.song_listbox = Listbox(
            self.window,
            bg="#ADADBB",
            fg="black",
            font=("Open Sans", 16),
            selectbackground="#FF5733",
            selectforeground="white",
            height=7,
            width=45
        )
        self.song_listbox.place(x=150, y=50)
        for song in self.song_list:
            self.song_listbox.insert("end", song.split("/")[-1])
        self.song_listbox.bind("<<ListboxSelect>>", self.select_song)

    def create_buttons(self):
        ASSETS_PATH = Path(__file__).parent / "images"

        def relative_to_assets(path: str) -> Path:
            return ASSETS_PATH / Path(path)

        button_configs = [
            ("info", "button_1.png", self.show_info, 500, 330, 57, 57),
            ("voice", "button_2.png", self.start_voice_recognition, 135, 330, 153, 57),
            ("gesture", "button_3.png", self.start_gesture_recognition, 318, 330, 153, 57),
            ("stop", "button_4.png", self.stop_music, 190, 250, 50.53, 50.53),
            ("skip", "button_5.png", self.skip_music, 452.83, 250, 50.77, 50.26),
            ("previous", "button_6.png", self.previous_music, 257.31, 250, 50.53, 50.04),
            ("play", "button_7.png", self.play, 323, 250, 50.48, 50.48),
            ("pause", "button_8.png", self.pause_music, 387.56, 250, 50.48, 50.48),
        ]

        for name, image, command, x, y, w, h in button_configs:
            button_image = PhotoImage(file=relative_to_assets(image))
            button = Button(
                self.window,
                image=button_image,
                borderwidth=0,
                highlightthickness=0,
                command=command,
                relief="flat"
            )
            button.image = button_image  # Keep reference to avoid garbage collection
            button.place(x=x, y=y, width=w, height=h)
            self.buttons[name] = button

    def highlight_button(self, button):
        """Highlight a button for 2 seconds."""
        original_color = button.cget("bg")
        button.config(bg="yellow")
        self.window.after(2000, lambda: button.config(bg=original_color))

    def play(self):
        self.highlight_button(self.buttons["play"])
        self.play_music()

    def play_music(self):
        if self.paused:
            mixer.music.unpause()
        else:
            try:
                mixer.music.load(self.song_list[self.current_song_index])
                mixer.music.set_volume(self.current_volume)
                mixer.music.play()
                self.current_song_var.set(f"Playing: {self.song_list[self.current_song_index].split('/')[-1]}")
            except Exception as e:
                print("Error playing song:", e)
                self.current_song_var.set("Error playing song")
        self.paused = False

    def select_song(self, event):
        selected_index = self.song_listbox.curselection()
        if selected_index:
            self.current_song_index = selected_index[0]
            self.play_music()

    def pause_music(self):
        self.highlight_button(self.buttons["pause"])
        mixer.music.pause()
        self.paused = True

    def stop_music(self):
        self.highlight_button(self.buttons["stop"])

        mixer.music.stop()
        self.paused = False
        self.current_song_var.set("Stopped")

    def skip_music(self):
        self.highlight_button(self.buttons["skip"])

        self.current_song_index = (self.current_song_index + 1) % len(self.song_list)
        self.update_listbox_selection()
        self.play_music()

    def previous_music(self):
        self.highlight_button(self.buttons["previous"])

        self.current_song_index = (self.current_song_index - 1) % len(self.song_list)
        self.update_listbox_selection()
        self.play_music()

    def lower_volume(self):
        print(self.current_volume)
        self.current_volume -= 0.1
        mixer.music.set_volume(self.current_volume)
        self.volume_slider.set(self.current_volume * 100)

    def increase_volume(self):
        self.current_volume += 0.1
        mixer.music.set_volume(self.current_volume)
        self.volume_slider.set(self.current_volume * 100)

    def update_volume(self, value):
        self.current_volume = float(value) / 100
        mixer.music.set_volume(self.current_volume)

    def show_info(self):
        print("Information button clicked")

    def start_voice_recognition(self):
        self.start_speech_recognition()

    def start_gesture_recognition(self):
        print("Gesture recognition started")

    def update_listbox_selection(self):
        self.song_listbox.selection_clear(0, "end")
        self.song_listbox.selection_set(self.current_song_index)
        self.song_listbox.activate(self.current_song_index)
        self.song_listbox.see(self.current_song_index)

    def start_speech_recognition(self):
        """Start the speech recognition in a separate thread."""
        threading.Thread(target=self.speech_recognition_thread, daemon=True).start()

    def speech_recognition_thread(self):
        """Thread function for speech recognition."""
        recognizer = sr.Recognizer()

        micro = sr.Microphone()
        print(micro.list_working_microphones())
        print(len(micro.list_working_microphones()))
        with sr.Microphone(0) as source:
            print("Speech recognition started. Say 'play', 'pause', 'resume', or 'stop' to control the player.")
            recognizer.adjust_for_ambient_noise(source)
            while True:
                try:



                    print("Listening...")

                    
                    audio = recognizer.listen(source)                        
    

                    command = recognizer.recognize_google(audio).lower()
                    #recognizer.recognize_tensorflow(audio_data=audio)
                    print(f"Recognized command: {command}")

                    if command in ["next", "skip"]:
                        self.skip_music()

                    if command in ["back", "previous"]:
                        self.previous_music()

                    if "play" in command:
                        self.play()
                    elif "pause" in command:
                        self.pause_music()
                    elif "resume" in command:
                        pass
                    elif "stop" in command:
                        
                        self.stop_music()
                    elif "quieter" in command or "lower volume" in command:

                        self.lower_volume()

                    elif "increase volume" in command:

                        self.increase_volume()
                        
                
                    else:
                        print("Unknown command.")
                except sr.UnknownValueError:
                    print("Could not understand the audio.")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")

    def drag_file(self, event):
        """Enable drag-and-drop within the listbox."""
        try:
        # Get the index of the item being dragged
            selected_index = self.file_listbox.curselection()[0]
            dragged_item = self.file_listbox.get(selected_index)

        # Find the target index based on the mouse position
            target_index = self.file_listbox.nearest(event.y)

        # Prevent dropping the item on itself
            if selected_index != target_index:
            # Remove the item and reinsert it at the target position
                self.file_listbox.delete(selected_index)
                self.file_listbox.insert(target_index, dragged_item)

            # Keep the selection on the moved item
                self.file_listbox.select_set(target_index)
        except IndexError:
            pass


if __name__ == "__main__":
    MediaPlayer(Tk())
