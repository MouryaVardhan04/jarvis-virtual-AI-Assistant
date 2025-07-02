import pyttsx3
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

engine = pyttsx3.init()

# Voice configuration
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[14].id)  # You can change index based on output
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def takecommand():
    fs = 16000  # Sample rate
    seconds = 5  # Duration of recording
    print("Recording...")

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write('output.wav', fs, myrecording)
    print("Recording finished, saved as output.wav")

    r = sr.Recognizer()
    with sr.AudioFile('output.wav') as source:
        audio = r.record(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print("User said:", query)
        return query.lower()
    except Exception as e:
        print("Sorry, could not recognize the audio.")
        return ""

# Main
text = takecommand()
if text:
    speak(text)
