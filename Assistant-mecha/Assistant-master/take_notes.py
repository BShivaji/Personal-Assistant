import pyautogui
import time
import subprocess
import speech_recognition as sr

def open_notepad():
    """Opens Notepad and brings it into focus."""
    try:
        subprocess.Popen("notepad.exe")  
        time.sleep(3) 
        print("✅ Notepad opened and ready for notes.")
    except Exception as e:
        print(f"❌ Error opening Notepad: {e}")

def take_notes():
    """Takes notes by converting speech to text and typing into Notepad."""
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("🎤 Speak now, I am taking notes (You have 10 seconds)...")
        recognizer.adjust_for_ambient_noise(source)

        try:
            audio = recognizer.listen(source, timeout=10)  
            note_text = recognizer.recognize_google(audio)
            print(f"📝 You said: {note_text}")

            time.sleep(1)
            pyautogui.click(x=1146, y=300)  
            time.sleep(1)
            pyautogui.typewrite(note_text, interval=0.05)  
            pyautogui.press("enter")
        except sr.WaitTimeoutError:
            print("⏳ Timeout: No speech detected.")
        except sr.UnknownValueError:
            print("❌ Sorry, I could not understand the audio.")
        except sr.RequestError:
            print("❌ Error with the speech recognition service.")

if __name__ == "__main__":
    open_notepad()
    take_notes()
