import os
import eel

from engine.features import *

eel.init("www")

playAssistantSound()

os.system('open index.html')  # correct for macOS

eel.start("index.html", mode="default", host="localhost", block=True)