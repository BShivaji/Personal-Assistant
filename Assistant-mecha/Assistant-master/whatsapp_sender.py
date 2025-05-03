import pywhatkit as pwk
import pyautogui
import time

def send_whatsapp_message(phone_number, message):
    """Sends a WhatsApp message instantly using PyWhatKit and presses 'Enter' to send."""
    try:
        print(f"📢 Preparing to send message to {phone_number}...")

        # Open WhatsApp Web and type the message
        pwk.sendwhatmsg_instantly(phone_number, message, wait_time=10, tab_close=False, close_time=10)

        # Wait for WhatsApp Web to load
        time.sleep(5)

        # Ensure chat box is focused and press "Enter" to send
        pyautogui.press("enter")
        
        print(f"✅ Message sent successfully to {phone_number}")
        return True
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False
