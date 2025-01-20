from pathlib import Path
from tkinter import Tk, Canvas, Label, StringVar, Button, PhotoImage, Scale, Listbox, HORIZONTAL
from pygame import mixer

# Initialisierung des Mixers für die Musikwiedergabe
mixer.init()

# Globale Variablen für Lautstärke, Wiedergabestatus und aktuelle Songindex
current_volume = 0.5
paused = False
current_song_index = 0

# Liste der Musikdateien (Pfad zu den MP3-Dateien)
OUTPUT_PATH = Path(__file__).parent
SONGS_PATH = OUTPUT_PATH / "songs"
song_list = [
    str(SONGS_PATH / "flow-211881.mp3"),
    str(SONGS_PATH / "amalgam-217007.mp3"),
    str(SONGS_PATH / "in-slow-motion-inspiring-ambient-lounge-219592.mp3"),
    str(SONGS_PATH / "nightfall-future-bass-music-228100.mp3"),
    str(SONGS_PATH / "perfect-beauty-191271.mp3")
]

# -------------------------------------
# Funktionen zur Steuerung der Musikwiedergabe
# -------------------------------------

def play_music():
    """Spielt den aktuellen Song ab oder setzt die Wiedergabe fort, wenn pausiert."""
    global paused, current_song_index
    if paused:
        mixer.music.unpause()
    else:
        try:
            # Laden und Abspielen des aktuellen Lieds
            mixer.music.load(song_list[current_song_index])
            mixer.music.set_volume(current_volume)
            mixer.music.play()
            # Anzeige des aktuell gespielten Songs
            current_song_var.set(f"Playing: {song_list[current_song_index].split('/')[-1]}")
        except Exception as e:
            print("Error playing song:", e)
            current_song_var.set("Error playing song")
    paused = False

def select_song(event):
    """Wählt einen Song aus der Liste aus und spielt ihn ab."""
    global current_song_index
    selected_index = song_listbox.curselection()
    if selected_index:
        current_song_index = selected_index[0]
        play_music()

def pause_music():
    """Pausiert die Wiedergabe der Musik."""
    global paused
    mixer.music.pause()
    paused = True

def stop_music():
    """Stoppt die Musikwiedergabe und setzt den Status zurück."""
    global paused
    mixer.music.stop()
    paused = False
    current_song_var.set("Stopped")

def skip_music():
    """Springt zum nächsten Song in der Liste."""
    global current_song_index
    current_song_index = (current_song_index + 1) % len(song_list)
    # Aktualisiert die Auswahl in der Listbox und spielt den Song ab
    song_listbox.selection_clear(0, "end")
    song_listbox.selection_set(current_song_index)
    song_listbox.activate(current_song_index)
    song_listbox.see(current_song_index)
    play_music()

def previous_music():
    """Springt zum vorherigen Song in der Liste."""
    global current_song_index
    current_song_index = (current_song_index - 1) % len(song_list)
    # Aktualisiert die Auswahl in der Listbox und spielt den Song ab
    song_listbox.selection_clear(0, "end")
    song_listbox.selection_set(current_song_index)
    song_listbox.activate(current_song_index)
    song_listbox.see(current_song_index)
    play_music()

def update_volume(value):
    """Aktualisiert die Lautstärke basierend auf dem Sliderwert."""
    global current_volume
    current_volume = float(value) / 100
    mixer.music.set_volume(current_volume)

def show_info():
    """Behandelt den Klick auf den Informationsbutton."""
    print("Information button clicked")

def start_voice_recognition():
    """Startet die Sprachsteuerung (Stub)."""
    print("Voice recognition started")

def start_gesture_recognition():
    """Startet die Gestensteuerung (Stub)."""
    print("Gesture recognition started")

# -------------------------------------
# Aufbau des Hauptfensters und Layout-Konfiguration
# -------------------------------------
window = Tk()
window.geometry("700x500")
window.configure(bg="#5C5C68")
window.resizable(False, False)

# Variable zur Anzeige des aktuell spielenden Songs
current_song_var = StringVar()
current_song_var.set("Not playing")

# Label zur Anzeige des aktuellen Songs
song_label = Label(
    window,
    textvariable=current_song_var,
    font=("Open Sans", 16),
    fg="white",
    bg="#19191D"
)
song_label.place(x=50, y=20)

# Festlegen des Pfades für Assets (Bilder etc.)
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "images"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)
    """Hilfsfunktion, um den relativen Pfad für Asset-Dateien zu erhalten."""
   

# -------------------------------------
# Canvas-Einrichtung für grafische Elemente
# -------------------------------------
canvas = Canvas(
    window,
    bg="#5C5C68",
    height=400,
    width=700,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

# -------------------------------------
# Lautstärkeregler (Volume Slider)
# -------------------------------------
volume_slider = Scale(
    window,
    from_=0,
    to=100,
    orient="vertical",
    length=250,
    bg="#ADADBB",
    troughcolor="#FFFFFF",
    command=update_volume
)
volume_slider.set(current_volume * 100)
volume_slider.place(x=50, y=50)

# -------------------------------------
# Buttons mit Bildern und ihren Befehlen
# -------------------------------------
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=show_info,
    relief="flat"
)
button_1.place(x=500, y=330, width=57, height=57)

button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=start_voice_recognition,
    relief="flat"
)
button_2.place(x=135, y=330, width=153, height=57)

button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=start_gesture_recognition,
    relief="flat"
)
button_3.place(x=318, y=330, width=153, height=57)

button_image_4 = PhotoImage(file=relative_to_assets("button_4.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=stop_music,
    relief="flat"
)
button_4.place(x=190, y=250, width=50.53, height=50.53)

button_image_5 = PhotoImage(file=relative_to_assets("button_5.png"))
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=skip_music,
    relief="flat"
)
button_5.place(x=452.83, y=250, width=50.77, height=50.26)

button_image_6 = PhotoImage(file=relative_to_assets("button_6.png"))
button_6 = Button(
    image=button_image_6,
    borderwidth=0,
    highlightthickness=0,
    command=previous_music,
    relief="flat"
)
button_6.place(x=257.31, y=250, width=50.53, height=50.04)

button_image_7 = PhotoImage(file=relative_to_assets("button_7.png"))
button_7 = Button(
    image=button_image_7,
    borderwidth=0,
    highlightthickness=0,
    command=play_music,
    relief="flat"
)
button_7.place(x=323, y=250, width=50.48, height=50.48)

button_image_8 = PhotoImage(file=relative_to_assets("button_8.png"))
button_8 = Button(
    image=button_image_8,
    borderwidth=0,
    highlightthickness=0,
    command=pause_music,
    relief="flat"
)
button_8.place(x=387.56, y=250, width=50.48, height=50.48)

# -------------------------------------
# Listbox zur Anzeige der Songliste
# -------------------------------------
song_listbox = Listbox(
    window,
    bg="#ADADBB",
    fg="black",
    font=("Open Sans", 16),
    selectbackground="#FF5733",
    selectforeground="white",
    height=7,
    width=45
)
# Positionierung der Listbox
song_listbox.place(x=150, y=50)

# Füllen der Listbox mit den Songtiteln
for song in song_list:
    formatted_song = "   " + song.split("/")[-1]
    song_listbox.insert("end", song.split("/")[-1])

# Verknüpfen des Listbox-Auswahlereignisses mit der Funktion select_song
song_listbox.bind("<<ListboxSelect>>", select_song)

# Hauptschleife des Tkinter-Fensters starten
window.mainloop()
