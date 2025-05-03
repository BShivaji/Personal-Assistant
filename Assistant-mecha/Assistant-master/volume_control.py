import pyautogui
import time

def increase_volume(steps=5):
    """Increase system volume by pressing the volume up key multiple times."""
    for _ in range(steps):
        pyautogui.press("volumeup")
        time.sleep(0.1) 

def decrease_volume(steps=5):
    """Decrease system volume by pressing the volume down key multiple times."""
    for _ in range(steps):
        pyautogui.press("volumedown")
        time.sleep(0.1)

def mute_volume():
    """Mute or unmute system volume."""
    pyautogui.press("volumemute")
