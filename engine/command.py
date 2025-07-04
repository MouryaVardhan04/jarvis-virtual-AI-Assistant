import pyttsx3
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import eel
import time
import os

# ✅ Initialize engine globally
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Try to set a specific voice, fallback to first available if index doesn't exist
try:
    if len(voices) > 14:
        engine.setProperty('voice', voices[14].id)
    else:
        engine.setProperty('voice', voices[0].id)
except Exception:
    # If voice setting fails, use the first available voice
    if voices:
        engine.setProperty('voice', voices[0].id)

engine.setProperty('rate', 180)
engine.setProperty('volume', 1.0)

def speak(text):
    print(f"[Speaking]: {text}")
    engine.say(text)
    engine.runAndWait()

def safe_eel_call(func_name, *args):
    """Safely call Eel functions, with fallback if not available"""
    try:
        if func_name == "DisplayMessage":
            eel.DisplayMessage(*args) # type : ignore
        elif func_name == "showHood":
            eel.showHood() # type : ignore
    except Exception as e:
        print(f"Eel call failed for {func_name}: {e}")

@eel.expose
def takecommand():
    fs = 16000
    seconds = 5
    print("Recording...")
    safe_eel_call("DisplayMessage", "Listening...")

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write('output.wav', fs, myrecording)
    print("Recording finished.")

    r = sr.Recognizer()
    with sr.AudioFile('output.wav') as source:
        audio = r.record(source)

    try:
        print("Recognizing...")
        safe_eel_call("DisplayMessage", "Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print("User said:", query)
        safe_eel_call("DisplayMessage", query)

        speak(query)
        time.sleep(0.3)  # ✅ Short pause before UI switch

        # Process the command directly here instead of calling allCommands
        processCommand(query)
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, could not recognize the audio.")
        safe_eel_call("DisplayMessage", "Sorry, I couldn't understand.")
        safe_eel_call("showHood")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        safe_eel_call("DisplayMessage", "Sorry, there was an error with the speech recognition service.")
        safe_eel_call("showHood")
        return ""
    except Exception as e:
        print(f"Error: {e}")
        safe_eel_call("DisplayMessage", "Sorry, an unexpected error occurred.")
        safe_eel_call("showHood")
        return ""

def processCommand(query):
    """Process commands and provide responses"""
    query = query.lower()
    print("Command received:", query)
    
    if "open" in query:
        from engine.features import openCommand
        openCommand(query)
        time.sleep(1)
        safe_eel_call("showHood")

    elif "on youtube" in query:
        from engine.features import PlayYoutube
        PlayYoutube(query)
        time.sleep(1)
        safe_eel_call("showHood")

    elif "hello" in query or "hi" in query:
        response = "Hello! How can I help you?"
        print(response)
        safe_eel_call("DisplayMessage", response)
        speak(response)
        time.sleep(1)
        safe_eel_call("showHood")

    elif "time" in query:
        import datetime
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        response = f"Current time is {current_time}"
        print(response)
        safe_eel_call("DisplayMessage", response)
        speak(response)
        time.sleep(1)
        safe_eel_call("showHood")

    elif "date" in query:
        import datetime
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        response = f"Today is {current_date}"
        print(response)
        safe_eel_call("DisplayMessage", response)
        speak(response)
        time.sleep(1)
        safe_eel_call("showHood")

    else:
        response = "I don't understand that command"
        print(response)
        safe_eel_call("DisplayMessage", response)
        speak(response)
        time.sleep(1)
        safe_eel_call("showHood")

@eel.expose
def allCommands(query=""):
    """Exposed function for frontend to call directly"""
    if not query:
        print("No command received")
        safe_eel_call("DisplayMessage", "No command received")
        return
    
    processCommand(query)

@eel.expose
def display_done():
    """Called by frontend when display animation is complete"""
    print("✅ Frontend finished displaying message")

