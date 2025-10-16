import pyttsx3
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import eel
import time
import os
import datetime # Import for time/date features

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
    seconds = 4 # Reduced time to 4 seconds for a quicker cycle
    r = sr.Recognizer()
    
    # 🌟 FIX: Use the Microphone as the source for immediate calibration 
    # and then capture, which is more reliable than writing to file first.
    # However, since you are using sounddevice/wav for recording, we'll 
    # stick to that but use the Recognizer's file processing.

    try:
        # Step 1: Record the audio to a file
        print("Recording...")
        safe_eel_call("DisplayMessage", "Listening...")

        # NOTE: You MUST speak *after* this message appears.
        # For better UX, you might want to record a moment of silence first 
        # for adjustment, but we'll try to rely on the Recognizer's internal 
        # energy threshold for now to keep the flow simple.
        
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        wav.write('output.wav', fs, myrecording)
        print("Recording finished.")

        # Step 2: Recognize the audio from the file
        with sr.AudioFile('output.wav') as source:
            # 🌟 IMPORTANT FIX: Adjust for ambient noise using the *recorded* file
            # This helps set the noise floor correctly.
            r.adjust_for_ambient_noise(source, duration=0.5) 
            # source.seek(0) # Rewind to the start of the file after adjustment
            
            audio = r.record(source)

        print("Recognizing...")
        safe_eel_call("DisplayMessage", "Recognizing...")
        
        # NOTE: You can also try a longer timeout for the API call if it's slow
        query = r.recognize_google(audio, language='en-in') 
        
        print("User said:", query)
        safe_eel_call("DisplayMessage", query)

        speak(query)
        time.sleep(0.3) 

        # Process the command
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
    finally:
        # Ensure the recorded file is cleaned up after use
        if os.path.exists('output.wav'):
            os.remove('output.wav')


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
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        response = f"Current time is {current_time}"
        print(response)
        safe_eel_call("DisplayMessage", response)
        speak(response)
        time.sleep(1)
        safe_eel_call("showHood")

    elif "date" in query:
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