import pvporcupine
import pyaudio
import speech_recognition as sr

# Your Picovoice Access Key (replace with your actual key)
ACCESS_KEY = "qa5ZHrh1k5xg/6zoy6ohsHg4e2S5JP/AAsp0LiHw2nxRCX51MZAnZQ=="

def listen_for_command():
    """
    Listens to the user's voice after wake word detection
    and converts it to text using Google Speech Recognition.
    """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Listening for a command...")

    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)  # Listen with a timeout of 5 seconds
            command = recognizer.recognize_google(audio)
            print(f"Command detected: {command}")
            return command.lower()  # Return the command in lowercase for easy matching
    except sr.WaitTimeoutError:
        print("No command detected (timeout).")
    except sr.UnknownValueError:
        print("Could not understand the audio.")
    except sr.RequestError as e:
        print(f"Speech Recognition error: {e}")
    return None

def process_command(command):
    """
    Processes the recognized speech command.
    """
    if "volume up" in command:
        print("Action: Volume increased.")
    elif "volume down" in command:
        print("Action: Volume decreased.")
    else:
        print("Unknown command.")

def main():
    """
    Main function to handle wake word detection and command processing.
    """
    # Initialize Porcupine for wake word detection
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keywords=[ "quieter"]  # Replace with a custom keyword if needed
    )

    # Setup PyAudio for microphone input
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("Listening for wake word...")

    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = [int.from_bytes(pcm[i:i+2], 'little', signed=True) for i in range(0, len(pcm), 2)]

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                command = listen_for_command()
                if command:
                    process_command(command)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

if __name__ == "__main__":
    main()
