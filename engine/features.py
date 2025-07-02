import pygame
import os
import eel


@eel.expose
#playing assistent
def playAssistantSound():
    pygame.mixer.init()
    pygame.mixer.music.load("www/assets/audio/start_sound.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

os.system('afplay /System/Library/Sounds/Glass.aiff')