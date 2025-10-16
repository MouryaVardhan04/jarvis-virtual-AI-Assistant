import pyttsx3
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import eel
import time
import os
import datetime # Import for time/date features

# NOTE: Using the API key provided by the user for demonstration.
# In a real environment, this should be kept secure.
GEMINI_API_KEY = "AIzaSyAoE9iIeJc09x-Ul2xInVBoNrCPiikiVbs"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

# ✅ Initialize engine globally
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# --- VOICE CUSTOMIZATION START (Guaranteed Female Voice) ---
def set_sweet_girl_voice(engine, voices):
    """
    Selects the first available voice explicitly marked as female.
    """
    selected_voice_id = None
    
    # 1. Search for ANY voice explicitly marked as Female, prioritizing English speakers
    
    # Prioritized English female voices
    english_female_ids = []
    
    for voice in voices:
        # Check if the gender is explicitly female
        is_female = voice.gender == ['VoiceGenderFemale']
        
        # Check if it's an English voice (US, AU, GB, etc.)
        is_english = voice.name.lower().startswith('en')

        if is_female and is_english:
            # Found a preferred English female voice
            selected_voice_id = voice.id
            print(f"[Voice] Found and set preferred voice: {voice.name} (ID: {voice.id})")
            break
        elif is_female:
            # Collect non-English female voices as a secondary fallback
            english_female_ids.append(voice.id)

    # 2. Fallback to any collected female voice if no English one was selected
    if not selected_voice_id and english_female_ids:
        selected_voice_id = english_female_ids[0]
        print(f"[Voice] Falling back to the first non-English female voice.")
    
    # 3. Final Fallback (if no female voice was found at all)
    if not selected_voice_id and voices:
        selected_voice_id = voices[0].id
        print(f"[Voice] Warning: No explicit female voice found. Falling back to default: {voices[0].name}")

    # 4. Apply the voice ID
    if selected_voice_id:
        try:
            engine.setProperty('voice', selected_voice_id)
        except Exception as e:
            print(f"[Voice Error] Failed to set voice property: {e}")
            if voices:
                engine.setProperty('voice', voices[0].id) 

set_sweet_girl_voice(engine, voices)
# --- VOICE CUSTOMIZATION END ---

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

# --- GEMINI API INTEGRATION START ---
def get_gemini_response(user_query):
    """Fetches a friendly, conversational response from the Gemini API."""
    
    system_prompt = (
        "You are a friendly, concise, and helpful virtual assistant named JARVIS. "
        "Keep your responses short, conversational, and avoid sounding too formal. "
        "If the user asks a question, answer it directly and warmly."
    )
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "tools": [{"google_search": {}}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }

    try:
        import requests
        headers = {'Content-Type': 'application/json'}
        
        # Use a short timeout for responsiveness
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", 
            json=payload, 
            headers=headers,
            timeout=10
        )
        response.raise_for_status() # Raise exception for bad status codes
        
        data = response.json()
        
        # Extract the text from the response
        text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")
        
        if text:
            return text.strip()
        else:
            return "I contacted my AI core, but it didn't give me a clear answer right now. Sorry!"

    except requests.exceptions.Timeout:
        return "I'm having trouble reaching the network right now. Maybe try again in a moment?"
    except requests.exceptions.RequestException as e:
        print(f"Gemini API Request Error: {e}")
        return "Oops, I ran into an error trying to process that request."
    except Exception as e:
        print(f"General AI Error: {e}")
        return "I'm experiencing a minor system hiccup. Can you try phrasing that differently?"
# --- GEMINI API INTEGRATION END ---


@eel.expose
def takecommand():
    fs = 16000
    seconds = 4 # Time to record the command
    r = sr.Recognizer()
    output_filename = 'output.wav'
    
    # 🌟 FIX: Use manual threshold for better reliability, especially on macOS
    r.energy_threshold = 200 
    
    try:
        # Step 1: Record the audio to a file
        print("Recording...")
        safe_eel_call("DisplayMessage", "Listening...")

        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        wav.write(output_filename, fs, myrecording)
        print("Recording finished.")

        # Step 2: Recognize the audio from the file
        with sr.AudioFile(output_filename) as source:
            audio = r.record(source) 

        print("Recognizing...")
        safe_eel_call("DisplayMessage", "Recognizing...")
        
        # Recognize using Google API
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
        if os.path.exists(output_filename):
            os.remove(output_filename)


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
        # 🌟 NEW AI CONVERSATION: Send unknown commands to Gemini
        print("Sending query to AI...")
        safe_eel_call("DisplayMessage", "Thinking...")
        ai_response = get_gemini_response(query)
        
        print("AI Response:", ai_response)
        safe_eel_call("DisplayMessage", ai_response)
        speak(ai_response)
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
