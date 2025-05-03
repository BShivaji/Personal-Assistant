

from typing import Self
import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import os
import webbrowser
import pyjokes
import pywhatkit as kit
import time
from plyer import notification 
import tkinter as tk
from tkinter import ttk, Scrollbar, Text, VERTICAL, END, NORMAL, DISABLED 
from tkinter import LEFT, BOTH, SUNKEN, W, E 
from PIL import Image, ImageTk
from threading import Thread
import pyautogui
import imdb
import playsound
import smtplib
import take_notes
from deep_translator import GoogleTranslator
from gtts import gTTS
from whatsapp_sender import send_whatsapp_message
from brightness_control import increase_brightness, decrease_brightness
from volume_control import increase_volume, decrease_volume , mute_volume
from system_status import get_system_status
from image_generator import generate_image
import OpenAi_requestAPI as ai
from email.message import EmailMessage
from decouple import config
from online import (find_my_ip, get_news,
                    weather_forecate)



BG_COLOR = "#242526"
BUTTON_COLOR = "#3a7bfc"
BUTTON_HOVER_COLOR = "#2962ff"
BUTTON_FONT = ("Helvetica", 11, "bold")
BUTTON_FOREGROUND = "white"
HEADING_FONT = ("Helvetica", 24, "bold")
INSTRUCTION_FONT = ("Helvetica", 11)
TEXT_COLOR = "#e0e0e0"
ENTRY_BG = "#3b3b3b"
ENTRY_FG = "white"
RESULT_BG = "#3b3b3b"
RESULT_FG = "lightgrey"
LISTENING_COLOR = "#4CAF50" 
RECOGNIZING_COLOR = "#FFC107" 


engine = None
dialog_active = False 
listening_label = None 
recognizing_label = None 
result_display = None 

def init_engine():
    global engine
    try:
        engine = pyttsx3.init()
        engine.setProperty('volume', 0.8)
        engine.setProperty('rate', 190)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[2].id) 
        print("Text-to-speech engine initialized.")
    except Exception as e:
        print(f"Failed to initialize pyttsx3: {e}")
        engine = None

def speak(text):
    global stop_flag, task_interrupted, engine
    if stop_flag or task_interrupted:
        print("Speech interrupted.")
        return

    print(f"Speaking: {text}")

    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error in speak function: {e}")
            reinit_engine()

def reinit_engine():
    global engine
    print("Re-initializing text-to-speech engine...")
    try:
        if engine is not None:
            try:
                engine.stop()
            except Exception as e:
                print(f"Error stopping engine during reinit: {e}")
        engine = pyttsx3.init()
        engine.setProperty('volume', 0.8)
        engine.setProperty('rate', 190)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[2].id) 
        print("Text-to-speech engine re-initialized.")
    except Exception as e:
        print(f"Failed to reinitialize pyttsx3: {e}")
        engine = None

def take_screenshot():
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_path = f"screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        speak(f"Screenshot saved as {screenshot_path}")
        print(f"Screenshot saved as {screenshot_path}")
    except Exception as e:
        speak("Failed to take a screenshot.")
        print(f"Error taking screenshot: {e}")

def get_movie_info(movie_name):
    try:
        movies_db = imdb.IMDb()
        movies = movies_db.search_movie(movie_name)

        if not movies:
            return "Sorry, I couldn't find any movie with that name."

        movie = movies[0]
        movie_info = movies_db.get_movie(movie.getID())

        title = movie["title"]
        year = movie.get("year", "Unknown Year")
        rating = movie_info.get("rating", "Not available")
        cast = [str(actor) for actor in movie_info.get("cast", [])[:3]]
        plot = movie_info.get("plot outline", ["Plot not available"])[0]

        return f"Title: {title} ({year})\nIMDB Rating: {rating}\nTop Cast: {', '.join(cast)}\nPlot: {plot}"
    except Exception as e:
        print(f"Error fetching movie details: {e}")
        return "Error fetching movie details. Please check your internet connection and movie name."

task_interrupted = False
entry = None
stop_flag = False
root = None
USER = config('USER')
HOSTNAME = config('BOT')

def wish_time():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 6:
        speak('Good night! Sleep tight.')
    elif 6 <= hour < 12:
        speak('Good morning!')
    elif 12 <= hour < 18:
        speak('Good afternoon!')
    else:
        speak('Good evening!')
    speak(f"Hello {USER}, I am {HOSTNAME}. How can I help you today?")

def take_command():
    global query, task_interrupted, dialog_active, listening_label, recognizing_label
    if dialog_active:
        print("Dialog active, skipping command listening.")
        return ""

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.8)

        if listening_label: 
            listening_label.config(text="Listening...", bg=LISTENING_COLOR, fg="white") # Set text color to white for visibility
        if recognizing_label: 
            recognizing_label.config(text="", bg=BG_COLOR)

        print("Listening...")
        r.pause_threshold = 2.0
        try:
            audio = r.listen(source, phrase_time_limit=25)

            if listening_label: 
                listening_label.config(text="", bg=BG_COLOR)
            if recognizing_label: 
                recognizing_label.config(text="Recognizing...", bg=RECOGNIZING_COLOR, fg="white") # Set text color to white for visibility

            print("Recognizing...") 
            query = r.recognize_google(audio, language='en-in').lower()
            print(f"User said: {query}")

            if recognizing_label: 
                recognizing_label.config(text="", bg=BG_COLOR)

            if 'stop' in query or 'cancel' in query or 'terminate' in query:
                stop_voice_assistant()
                return ""
            elif 'exit' in query or 'quit' in query or 'bye' in query:
                stop_voice_assistant()
                return ""

            return query

        except sr.WaitTimeoutError:
            print("Listening timed out (WaitTimeoutError - should not happen without timeout).")
            if listening_label: 
                listening_label.config(text="", bg=BG_COLOR)
            if recognizing_label: 
                recognizing_label.config(text="", bg=BG_COLOR)
            return ""
        except sr.UnknownValueError:
            speak("Sorry, I could not understand. Please repeat.")
            if listening_label: 
                listening_label.config(text="", bg=BG_COLOR)
            if recognizing_label: 
                recognizing_label.config(text="", bg=BG_COLOR)
            return ""
        except sr.RequestError as e:
            print(f"Speech recognition request error: {e}")
            speak("Sorry, speech service is currently unavailable. Please check your internet connection.")
            if listening_label: 
                listening_label.config(text="", bg=BG_COLOR)
            if recognizing_label: 
                recognizing_label.config(text="", bg=BG_COLOR)
            return ""
        except Exception as e:
            print(f"Speech recognition error: {e}")
            speak("An error occurred during speech recognition.")
            if listening_label: 
                listening_label.config(text="", bg=BG_COLOR)
            if recognizing_label: 
                recognizing_label.config(text="", bg=BG_COLOR)
            return ""


def send_mail(receiver_email, subject, message):
    try:
        sender_email = config('EMAIL_USER')
        sender_password = config('EMAIL_PASS')

        if not sender_email or not sender_password:
            print("Error: Email credentials missing in .env file!")
            speak("Email setup is not configured correctly. Please check the .env file.")
            return False

        print(f"Attempting to send email from: {sender_email} to: {receiver_email}")

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg.set_content(message)

        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()

            print("Attempting to login to email server...")
            server.login(sender_email, sender_password)
            print("Login successful, sending message...")

            server.send_message(msg)

        print("Email sent successfully!")
        speak("Email sent successfully!")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        speak("Email authentication failed. Please check your email and app password.")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"SMTP Connection Error: {e}")
        speak("Could not connect to the email server. Please check your internet connection.")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}")
        speak("An error occurred while sending the email.")
        return False
    except Exception as e:
        print(f"Unexpected Email Error: {str(e)}")
        speak("An unexpected error occurred with email sending.")
        return False

class EmailDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Send Email")
        self.geometry("400x520")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        global dialog_active
        dialog_active = True
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        main_frame = tk.Frame(self, bg=BG_COLOR, padx=20, pady=20)
        main_frame.pack(expand=True, fill=BOTH)

        fields = [
            ("To:", "to_email"),
            ("Subject:", "subject"),
            ("Message:", "message")
        ]

        self.entries = {}
        for label_text, field_name in fields:
            label = tk.Label(
                main_frame,
                text=label_text,
                font=INSTRUCTION_FONT,
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                anchor="w",
                justify=LEFT
            )
            label.pack(fill="x", pady=(5, 2))

            if field_name == "message":
                entry = tk.Text(
                    main_frame,
                    height=8,
                    font=INSTRUCTION_FONT,
                    bg=ENTRY_BG,
                    fg=ENTRY_FG,
                    relief="flat",
                    highlightthickness=1,
                    highlightbackground=BUTTON_COLOR,
                    highlightcolor=BUTTON_COLOR
                )
            else:
                entry = tk.Entry(
                    main_frame,
                    font=INSTRUCTION_FONT,
                    bg=ENTRY_BG,
                    fg=ENTRY_FG,
                    insertbackground=TEXT_COLOR,
                    relief="flat",
                    highlightthickness=1,
                    highlightbackground=BUTTON_COLOR,
                    highlightcolor=BUTTON_COLOR
                )

            entry.pack(fill="x", pady=(0, 8))
            self.entries[field_name] = entry

        self.entries["to_email"].focus_set()

        button_frame = tk.Frame(main_frame, bg=BG_COLOR)
        button_frame.pack(fill="x", pady=(15, 0))

        send_button = ModernButton(
            button_frame,
            text="Send Email",
            command=self.send_email
        )
        send_button.pack(side="left", expand=True, padx=5)

        cancel_button = ModernButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        )
        cancel_button.pack(side="right", expand=True, padx=5)

        self.bind('<Return>', lambda e: self.send_email())
        self.result = False

    def destroy(self):
        global dialog_active
        super().destroy()
        dialog_active = False

    def send_email(self):
        try:
            to_email = self.entries["to_email"].get()
            subject = self.entries["subject"].get()
            message = self.entries["message"].get("1.0", "end-1c")

            if not all([to_email, subject, message]):
                speak("Please fill in all fields")
                return

            if send_mail(to_email, subject, message):
                self.result = True
            else:
                speak("Failed to send email. Please check the console for details.")

            self.destroy()

        except Exception as e:
            print(f"Error sending email from dialog: {str(e)}")
            speak("Error sending email. Please check the console for details.")
            self.destroy()

class WeatherDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Weather Forecast")
        self.geometry("350x170")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        global dialog_active
        dialog_active = True
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        main_frame = tk.Frame(self, bg=BG_COLOR, padx=20, pady=20)
        main_frame.pack(expand=True, fill=BOTH)

        label = tk.Label(
            main_frame,
            text="Enter city name:",
            font=INSTRUCTION_FONT,
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor="w",
            justify=LEFT
        )
        label.pack(fill="x", pady=(5, 2))

        self.city_entry = tk.Entry(
            main_frame,
            font=INSTRUCTION_FONT,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            insertbackground=TEXT_COLOR,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BUTTON_COLOR,
            highlightcolor=BUTTON_COLOR
        )
        self.city_entry.pack(fill="x", pady=(0, 10))
        self.city_entry.focus_set()

        button_frame = tk.Frame(main_frame, bg=BG_COLOR)
        button_frame.pack(fill="x", pady=(15, 0))

        get_button = ModernButton(
            button_frame,
            text="Get Weather",
            command=self.submit_city,
            width=15
        )
        get_button.pack(side="left", expand=True, padx=5)

        cancel_button = ModernButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        )
        cancel_button.pack(side="right", expand=True, padx=5)

        self.bind('<Return>', lambda e: self.submit_city())

    def destroy(self):
        global dialog_active
        super().destroy()
        dialog_active = False

    def submit_city(self):
        city = self.city_entry.get().strip()
        if city:
            self.destroy()
            self.callback(city)
        else:
            speak("Please enter a city name")

class WhatsAppDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Send WhatsApp Message")
        self.geometry("400x420")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        global dialog_active
        dialog_active = True
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        main_frame = tk.Frame(self, bg=BG_COLOR, padx=20, pady=20)
        main_frame.pack(expand=True, fill=BOTH)

        fields = [
            ("Phone Number (with country code):", "phone"),
            ("Message:", "message")
        ]

        self.entries = {}
        for label_text, field_name in fields:
            label = tk.Label(
                main_frame,
                text=label_text,
                font=INSTRUCTION_FONT,
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                anchor="w",
                justify=LEFT
            )
            label.pack(fill="x", pady=(5, 2))

            if field_name == "message":
                entry = tk.Text(
                    main_frame,
                    height=6,
                    font=INSTRUCTION_FONT,
                    bg=ENTRY_BG,
                    fg=ENTRY_FG,
                    relief="flat",
                    highlightthickness=1,
                    highlightbackground=BUTTON_COLOR,
                    highlightcolor=BUTTON_COLOR
                )
            else:
                entry = tk.Entry(
                    main_frame,
                    font=INSTRUCTION_FONT,
                    bg=ENTRY_BG,
                    fg=ENTRY_FG,
                    insertbackground=TEXT_COLOR,
                    relief="flat",
                    highlightthickness=1,
                    highlightbackground=BUTTON_COLOR,
                    highlightcolor=BUTTON_COLOR
                )

            entry.pack(fill="x", pady=(0, 8))
            self.entries[field_name] = entry

        self.entries["phone"].focus_set()

        button_frame = tk.Frame(main_frame, bg=BG_COLOR)
        button_frame.pack(fill="x", pady=(15, 0))

        send_button = ModernButton(
            button_frame,
            text="Send Message",
            command=self.send_message,
            bg="#4CAF50",
            fg="white"
        )
        send_button.pack(side="left", expand=True, padx=5)

        cancel_button = ModernButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        )
        cancel_button.pack(side="right", expand=True, padx=5)

        self.entries["phone"].bind('<Return>', lambda e: self.entries["message"].focus_set())
        self.bind('<Control-Return>', lambda e: self.send_message())

    def destroy(self):
        global dialog_active
        super().destroy()
        dialog_active = False

    def send_message(self):
        try:
            phone = self.entries["phone"].get().strip()
            message = self.entries["message"].get("1.0", END).strip() 
            if not phone or not message:
                speak("Please fill in all fields")
                return

            self.destroy()
            self.callback(phone, message)
        except Exception as e:
            print(f"Error in WhatsApp dialog: {e}")
            speak("Error processing your request. Please check the console for details.")
            self.destroy()
            
class TranslateDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Translate Text")
        self.geometry("400x420")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        global dialog_active
        dialog_active = True
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel_translation)

        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        main_frame = tk.Frame(self, bg=BG_COLOR, padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        label_text = tk.Label(main_frame, text="Enter text to translate:", font=INSTRUCTION_FONT, bg=BG_COLOR, fg=TEXT_COLOR, anchor="w", justify=LEFT)
        label_text.pack(fill="x", pady=(5, 2))

        self.text_entry = tk.Text(main_frame, height=6, font=INSTRUCTION_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
        self.text_entry.pack(fill="x", pady=(0, 10))

        label_lang = tk.Label(main_frame, text="Enter target language code (e.g., 'en', 'es'):", font=INSTRUCTION_FONT, bg=BG_COLOR, fg=TEXT_COLOR, anchor="w", justify=LEFT)
        label_lang.pack(fill="x", pady=(5, 2))

        self.lang_entry = tk.Entry(main_frame, font=INSTRUCTION_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
        self.lang_entry.pack(fill="x", pady=(0, 10))

        button_frame = tk.Frame(main_frame, bg=BG_COLOR)
        button_frame.pack(fill="x", pady=(15, 0))

        self.translate_button = ModernButton(
            button_frame, text="Translate", command=self.translate_and_speak
        )
        self.translate_button.pack(side="left", expand=True, padx=5, pady=5)

        self.cancel_button = ModernButton(
            button_frame, text="Cancel", bg="red", command=self.cancel_translation
        )
        self.cancel_button.pack(side="right", expand=True, padx=5)

    def destroy(self):
        global dialog_active
        super().destroy()
        dialog_active = False

    def translate_and_speak(self):
        text_to_translate = self.text_entry.get("1.0", END).strip() 
        target_language = self.lang_entry.get().strip().lower()

        if not text_to_translate or not target_language:
            speak("Please enter text and target language code.")
            return

        try:
            translator = GoogleTranslator(source="auto", target=target_language)
            translated_text = translator.translate(text_to_translate)
            print(f"Translated: {translated_text}")

            tts = gTTS(text=translated_text, lang=target_language)
            audio_file = "translated_audio.mp3"
            tts.save(audio_file)

            playsound.playsound(audio_file)
            os.remove(audio_file)

            self.callback(translated_text)

        except Exception as e:
            print(f"Error during translation: {e}")
            speak("An error occurred during translation. Please check the console for details.")

        self.destroy()

    def cancel_translation(self):
        self.callback(None)
        self.destroy()


class MovieTicketDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Book Movie Ticket")
        self.geometry("450x450") 
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        global dialog_active
        dialog_active = True
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        main_frame = tk.Frame(self, bg=BG_COLOR, padx=20, pady=20)
        main_frame.pack(expand=True, fill=BOTH)

        fields = [
            ("Movie Name:", "movie_name"),
            ("City:", "city"),
            ("Country (India only):", "country")
        ]

        self.entries = {}
        for label_text, field_name in fields:
            label = tk.Label(
                main_frame,
                text=label_text,
                font=INSTRUCTION_FONT,
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                anchor="w",
                justify=LEFT
            )
            label.pack( fill="x", pady=(5, 2)) 

            if field_name == "country":
                
                self.country_var = tk.StringVar(value="India")
                entry = ttk.Combobox(
                    main_frame,
                    textvariable=self.country_var,
                    values=["India"], 
                    state="readonly", 
                    font=INSTRUCTION_FONT,
                    style="Custom.TCombobox" 
                )
                entry.pack(fill="x", pady=(0, 8))
                self.entries[field_name] = entry

            else:
                entry = tk.Entry(
                    main_frame,
                    font=INSTRUCTION_FONT,
                    bg=ENTRY_BG,
                    fg=ENTRY_FG,
                    insertbackground=TEXT_COLOR,
                    relief="flat",
                    highlightthickness=1,
                    highlightbackground=BUTTON_COLOR,
                    highlightcolor=BUTTON_COLOR
                )
                entry.pack(fill="x", pady=(0, 8))
                self.entries[field_name] = entry

        
        style = ttk.Style()
        style.configure("Custom.TCombobox",
                        background=ENTRY_BG,
                        foreground=ENTRY_FG,
                        fieldbackground=ENTRY_BG,
                        selectbackground=BUTTON_COLOR,
                        selectforeground=ENTRY_FG)
        style.map("Custom.TCombobox",
                  background=[("active", BUTTON_HOVER_COLOR), ("focus", BUTTON_COLOR)])


        self.entries["movie_name"].focus_set()

        button_frame = tk.Frame(main_frame, bg=BG_COLOR)
        button_frame.pack(fill="x", pady=(15, 0))

        book_button = ModernButton(
            button_frame,
            text="Book Ticket",
            command=self.book_ticket_action
        )
        book_button.pack(side="left", expand=True, padx=5)

        cancel_button = ModernButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        )
        cancel_button.pack(side="right", expand=True, padx=5)

        self.bind('<Return>', lambda e: self.book_ticket_action()) 

    def destroy(self):
        global dialog_active
        super().destroy()
        dialog_active = False

    def book_ticket_action(self):
        movie_name = self.entries["movie_name"].get().strip()
        city = self.entries["city"].get().strip().lower()
        country = self.country_var.get().strip().lower() 

        if not all([movie_name, city, country]):
            speak("Please fill in all fields for movie ticket booking.")
            return

        result_message = book_movie_ticket(movie_name, city, country)
        self.destroy()
        self.callback(result_message) 

def book_movie_ticket(movie_name, city, country):
    """Automates movie ticket booking using PyAutoGUI. Now takes input as arguments."""
    try:
        if country != "india":
            print("❌ Currently, this service is only available in India.")
            return "Sorry, ticket booking is only available for Indian cities."

        # Open BookMyShow for the selected city
        url = f"https://in.bookmyshow.com/explore/movies-{city.replace(' ', '-')}"
        webbrowser.open(url)
        time.sleep(5)  # Wait for page to load

        # Click on the search bar (Manually adjust coordinates - these might need adjustment based on screen)
        pyautogui.click(x=434, y=150)
        time.sleep(1)

        # Type movie name and press enter
        pyautogui.typewrite(movie_name, interval=0.1)
        pyautogui.press("enter")
        time.sleep(5)

        # Click first movie result (Manually adjust coordinates - these might need adjustment based on screen)
        pyautogui.click(x=628, y=246)
        time.sleep(5)

        # Click "Book Tickets" (Manually adjust coordinates - these might need adjustment based on screen)
        pyautogui.click(x=676, y=712)
        time.sleep(5)

        print(f"✅ Go through date and seats. Please confirm the payment manually.")
        return "Go through date and seats. Please confirm the payment manually." 

    except Exception as e:
        print(f"❌ Error booking ticket: {e}")
        return f"Error booking ticket: {e}. Please try again and ensure BookMyShow page is loaded correctly." 


def process_translation(translated_text):
    if translated_text:
        speak("Translation complete.")
        update_result_display(f"Translated text: {translated_text}")
        print(f"Translated: {translated_text}")
    else:
        speak("Translation cancelled.")

def close_application():
    speak("closing application")
    pyautogui.hotkey("alt", "f4")

def process_weather(city):
    try:
        speak(f"Getting weather report for {city}")
        update_result_display(f"Fetching weather for {city}...")
        weather, temp, feels_like, humidity = weather_forecate(city)
        result = f"Weather in {city}: {weather}\nTemperature: {temp}\nFeels like: {feels_like}\nHumidity: {humidity}"
        speak(f"The current weather in {city} is {weather} with a temperature of {temp}")
        update_result_display(result)
    except Exception as e:
        error_msg = f"Error fetching weather data: {str(e)}"
        speak("Sorry, I couldn't get the weather information. Please check the console for details.")
        update_result_display(error_msg)

def process_whatsapp(phone, message):
    try:
        speak(f"Sending WhatsApp message to {phone}")
        update_result_display(f"Sending WhatsApp message to {phone}...")
        if send_whatsapp_message(phone, message):
            result = f"WhatsApp message sent successfully to {phone}"
            speak("WhatsApp message sent successfully")
        else:
            result = "Failed to send WhatsApp message. Please check the console for details."
            speak("Failed to send WhatsApp message.")
        update_result_display(result)
    except Exception as e:
        error_msg = f"Error sending WhatsApp message: {str(e)}"
        speak("Sorry, I couldn't send the WhatsApp message. Please check the console for details.")
        update_result_display(error_msg)

def process_movie_booking_result(booking_result):
    speak(booking_result) 
    update_result_display(booking_result) 

def perform_task():
    global stop_flag, result_display, root
    macha_chat = []
    while not stop_flag:
        query = take_command().lower()
        if not query:
            continue

        if "weather" in query or "weather today" in query or "weather forecast" in query:
            speak("Please enter the city name")
            dialog = WeatherDialog(root, process_weather)
            root.wait_window(dialog)
            continue

        elif "send whatsapp message" in query or "whatsapp message" in query:
            speak("Okay, let's send a WhatsApp message.")
            dialog = WhatsAppDialog(root, process_whatsapp)
            root.wait_window(dialog)
            continue

        elif 'send email' in query:
            speak("Alright, let's compose an email.")
            dialog = EmailDialog(root)
            root.wait_window(dialog)
            update_result_display("Email Sent sucessfully!")
            continue

        elif "translate" in query:
            speak("Please wait a moment while I prepare the translation dialog...")

            def on_translation_complete(translated_text):
                if translated_text:
                    process_translation(translated_text)
                else:
                    speak("Translation canceled.")

            dialog = TranslateDialog(root, on_translation_complete)
            root.wait_window(dialog)
            continue

        elif "book movie ticket" in query or "book movie tickets" in query or "book movie" in query:
            speak("Okay, let's book movie tickets.")
            dialog = MovieTicketDialog(root, process_movie_booking_result)
            root.wait_window(dialog)
            continue

        elif "close application" in query or "close app" in query or "exit application" in query or "exit app" in query:
            close_application()
            update_result_display("Closing Application")
            continue

        elif "take notes" in query:
            speak("Opening Notepad and taking notes.")
            take_notes.open_notepad()
            time.sleep(1)
            take_notes.take_notes()
            update_result_display("Note taken and typed into Notepad.")
            continue

        elif "news" in query or "news today" in query:
            try:
                speak("Fetching the latest headlines for you.")
                update_result_display("Fetching news headlines...")
                news = get_news()

                if isinstance(news, list) and len(news) > 0:
                    news_text = "\n".join(news)
                    update_result_display(news_text)

                    speak("Here are today's top headlines.")
                    for i, headline in enumerate(news[:3]):
                        speak(headline)
                        time.sleep(0.3)
                else:
                    speak("Sorry, I couldn't fetch any news headlines right now.")
                    update_result_display("No news headlines available.")

            except Exception as e:
                error_msg = f"Error fetching news: {str(e)}"
                speak("Sorry, I encountered an error when fetching news. Please check the console for details.")
                update_result_display(error_msg)
                print(error_msg)

            continue

        if 'wikipedia' in query:
            speak('Searching Wikipedia for that...')
            query = query.replace("wikipedia", "").strip()
            if query:
                try:
                    results = wikipedia.summary(query, sentences=2)
                    speak("According to Wikipedia:")
                    update_result_display(results)
                    speak(results)
                except wikipedia.exceptions.PageError:
                    speak("Sorry, I couldn't find a Wikipedia page for that.")
                    update_result_display("No Wikipedia page found.")
                except wikipedia.exceptions.DisambiguationError as e:
                    speak(f"Wikipedia returned multiple results. Could you be more specific? Options include: {', '.join(e.options)}")
                    update_result_display(f"Wikipedia results ambiguous. Options: {', '.join(e.options)}")
                except Exception as e:
                    error_msg = f"Wikipedia error: {str(e)}"
                    speak("Sorry, I encountered an issue while searching Wikipedia. Please check the console for details.")
                    update_result_display(error_msg)
            else:
                speak("What would you like me to search on Wikipedia?")

        elif "open" in query:
            speak("Opening Application")
            query = query.replace("open", "").strip()
            pyautogui.hotkey("win")
            pyautogui.write(query, interval=0.05)
            pyautogui.press("enter")
            update_result_display(f"Opening {query}")

        elif "ip address" in query:
            try:
                ip_address = find_my_ip()
                speak(f"Your IP address is: {ip_address}")
                print(f"Your IP address is: {ip_address}")
                update_result_display(f"Your IP Address: {ip_address}")
            except Exception as e:
                error_msg = f"Error getting IP address: {str(e)}"
                speak("Sorry, I couldn't retrieve your IP address. Please check your internet connection.")
                update_result_display(error_msg)

        elif "new task" in query:
            task = query.replace("new task", "")
            task = task.strip()
            if task != "":
                speak("Adding task" + task)
                with open("to do.txt", "a") as file:
                    file.write(task + "\n")
            update_result_display(task)

        elif "speak task" in query:
            try:
                with open("to do.txt", "r") as file:
                    tasks = file.read().strip()
                    if tasks:
                        speak("Here are the tasks for today.")
                        speak(tasks)
                        update_result_display(f"Tasks:\n{tasks}")
                    else:
                        speak("There are no tasks at the moment.")
                        update_result_display("No tasks to show.")
            except Exception as e:
                speak("Sorry, I couldn't read the task list.")
                update_result_display(f"Error: {str(e)}")


        elif "clear task" in query:
            with open("to do.txt", "w") as file:
                file.write("")
                speak("List cleared")
            update_result_display("List is cleard")

        elif "show task" in query:
            try:
                with open("to do.txt", "r") as file:
                    tasks = file.read().strip()
                    if tasks:
                        speak("Here are your tasks.")
                        update_result_display(f"Tasks:\n{tasks}")
                        notification.notify(
                            title='Tasks List',
                            app_name='Macha Assistant',
                            message=tasks
                        )
                    else:
                        speak("You have no tasks at the moment.")
                        update_result_display("No tasks found.")
            except Exception as e:
                speak("Sorry, I couldn't access the task list.")
                update_result_display(f"Error reading task list: {str(e)}")


        elif "clear chat" in query:
            macha_chat = []
            speak("Chat cleared")

        elif "increase volume" in query:
            speak("Increasing volume now.")
            increase_volume()
            update_result_display("Volmue Increased")

        elif "decrease volume" in query:
            speak("Decreasing volume now.")
            decrease_volume()
            update_result_display("Volmue Decreased")

        elif "mute" in query or "mute volume" in query:
            speak("Muting volume.")
            mute_volume()
            update_result_display("muted")

        elif "increase brightness" in query:
            words = query.split()
            step = next((int(word) for word in words if word.isdigit()), None)
            response = increase_brightness(step)
            speak(response)
            update_result_display("Brightness Increased")

        elif "decrease brightness" in query:
            words = query.split()
            step = next((int(word) for word in words if word.isdigit()), None)
            response = decrease_brightness(step)
            speak(response)
            update_result_display("Brightness decreased")

        elif 'play' in query:
            song = query.replace('play', "", 1).strip()
            if song:
                speak(f"Playing {song} on YouTube.")
                kit.playonyt(song)
            else:
                speak("What song would you like me to play?")
            update_result_display(song)

        elif 'youtube' in query:
            speak("Opening YouTube.")
            webbrowser.open("https://www.youtube.com/")
            update_result_display("Opening YouTube")

        elif 'google' in query:
            speak("Opening Google.")
            webbrowser.open("https://www.google.com/")
            update_result_display("Opening Google")

        elif 'search' in query:
            search_term = query.replace('search', '', 1).strip()
            if search_term:
                speak(f"Searching Google for {search_term}.")
                kit.search(search_term)
            else:
                speak("What would you like me to search for?")
            update_result_display(f"Searching Google for {search_term}.")

        elif 'the time' in query:
            str_time = datetime.datetime.now().strftime("%I:%M %p")
            update_result_display(f"Current Time: {str_time}")
            speak(f"The current time is {str_time}")


        elif "system condition" in query or "system status" in query:
            speak("Checking system status for you.")
            status = get_system_status()
            update_result_display(status)
            speak(status)

        elif 'joke' in query:
            speak("Here's a joke for you.")
            joke = pyjokes.get_joke()
            speak(joke)
            update_result_display(joke)

        elif 'screenshot' in query:
            speak("Taking a screenshot.")
            take_screenshot()

        elif 'movie' in query:
            speak("Sure, which movie would you like information about?")
            movie_name = take_command()
            if movie_name and movie_name != "None":
                speak(f"Fetching movie information for {movie_name}.")
                movie_info = get_movie_info(movie_name)
                update_result_display(movie_info)
                speak(movie_info)
                print(movie_info)
            else:
                speak("Sorry, I didn't catch the movie name.")

        elif 'exit' in query or 'quit' in query or 'bye' in query:
            speak("Goodbye! Have a great day.")
            stop_voice_assistant()
            break

        elif "generate an image" in query or "show me an image" in query or "create an image" in query:
            prompt = query.replace(
                "generate an image of", "").replace(
                "show me an image of", "").replace(
                "generate image of", "").replace(
                "create an image of", "").replace(
                "generate an image", "").replace(
                "show me an image", "").replace(
                "create an image", "").strip()

            if prompt:
                speak(f"Generating an image of {prompt}. Please wait a moment.")
                update_result_display(f"Generating image of '{prompt}'...")
                try:
                    speak_msg, print_msg = generate_image(prompt)
                    update_result_display(print_msg)
                    speak(speak_msg)
                except Exception as e:
                    error_msg = f"Error generating image: {str(e)}"
                    speak("Sorry, there was an error generating the image. Please check the console for details.")
                    update_result_display(error_msg)
            else:
                speak("What kind of image would you like me to generate?")

        else:
            print(f"Query for AI: {query}")
            query_for_ai = query.replace("macha", "").strip()
            if query_for_ai:
                speak("Please wait, processing your request...")
                update_result_display("Processing AI request...")
                macha_chat.append({"role": "user", "content": query_for_ai})
                try:
                    response = ai.send_request(macha_chat)
                    macha_chat.append({"role": "assistant", "content": response})
                    speak(response)
                    print(f"AI Response: {response}")
                    update_result_display(response)
                except Exception as e:
                    error_msg = f"AI request error: {str(e)}"
                    speak("Sorry, I encountered an error communicating with the AI. Please check the console for details.")
                    update_result_display(error_msg)
                    print(error_msg)
            else:
                speak("Sorry, I didn't catch what you wanted to ask the AI.")


def stop_voice_assistant():
    global stop_flag, root
    print("Stopping voice assistant...")
    stop_flag = True
    try:
        if engine:
            engine.stop()
    except Exception as e:
        print(f"Error stopping engine: {e}")

def start_voice_assistant():
    global stop_flag
    try:
        stop_flag = False
        wish_time()
        perform_task()
    except Exception as e:
        print(f"Error in voice assistant main loop: {e}")
        update_result_display(f"Error: {str(e)}")
    finally:
        stop_flag = False

class ModernButton(tk.Button):
    def __init__(self, master=None, bg=BUTTON_COLOR, fg=BUTTON_FOREGROUND, **kwargs):
        super().__init__(master, **kwargs)
        self.default_bg = bg
        self.default_fg = fg
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.config(
            bg=self.default_bg,
            fg=self.default_fg,
            font=BUTTON_FONT,
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2"
        )

    def on_enter(self, e):
        if self.default_bg == BUTTON_COLOR:
            self.config(background=BUTTON_HOVER_COLOR)
        else:
            r, g, b = self.winfo_rgb(self.default_bg)
            darker = f"#{r//300:02x}{g//300:02x}{b//300:02x}"
            self.config(background=darker)

    def on_leave(self, e):
        self.config(background=self.default_bg)

def update_result_display(text):
    global result_display
    if result_display:
        result_display.config(state=NORMAL) 
        result_display.insert(END, text + "\n\n") 
        result_display.see(END) 
        result_display.config(state=DISABLED) 

button= None

def main():
    global root, entry, result_display, listening_label, recognizing_label, button
    root = tk.Tk()
    root.title(f"{HOSTNAME} Voice Assistant")
    root.geometry("550x750") 
    root.configure(bg=BG_COLOR)

    def on_closing():
        stop_voice_assistant()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    def on_button_click():
        global stop_flag, button 
        if button.cget('text') == "Start Assistant": 
            stop_flag = False
            update_result_display("Starting voice assistant...") 
            button.config(text="Stop Assistant") 
            Thread(target=start_voice_assistant).start()
        else: 
            stop_flag = True
            update_result_display("Stopping voice assistant...") 
            button.config(text="Start Assistant") 
            try:
                if engine:
                    engine.stop()
            except:
                pass

    background_image = Image.open("Assistant-master/wallpaperflare.com_wallpaper.jpg")
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = ttk.Label(root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    overlay = tk.Frame(root, bg=BG_COLOR)
    overlay.place(x=0, y=0, relwidth=1, relheight=1)

    main_frame = tk.Frame(overlay, bg=BG_COLOR, padx=30, pady=30)
    main_frame.pack(expand=True, fill=BOTH)

    profile_frame = tk.Frame(main_frame, bg=BG_COLOR)
    profile_frame.pack(pady=(15, 10))

    image2 = Image.open("Assistant-master/p.jpg")
    resized_image = image2.resize((120, 120))
    p2 = ImageTk.PhotoImage(resized_image)
    l2 = tk.Label(profile_frame, image=p2, bg=BG_COLOR)
    l2.pack()

    heading_label = tk.Label(
        main_frame,
        text=f"{HOSTNAME} Voice Assistant",
        font=HEADING_FONT,
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )
    heading_label.pack(pady=(10, 10))

    instruction_label = tk.Label(
        main_frame,
        text="Click to start voice commands",
        font=INSTRUCTION_FONT,
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )
    instruction_label.pack(pady=(5, 15))

    button = ModernButton(
        main_frame,
        text="Start Assistant",
        command=on_button_click,
        width=18
    )
    button.pack(pady=(10, 20))


    status_label_frame = tk.Frame(main_frame, bg=BG_COLOR)
    status_label_frame.pack(fill="x", pady=(0, 10)) 

    listening_label = tk.Label(status_label_frame, text="", font=INSTRUCTION_FONT, bg=BG_COLOR, fg="white") 
    listening_label.pack(side=LEFT, padx=10) 

    recognizing_label = tk.Label(status_label_frame, text="", font=INSTRUCTION_FONT, bg=BG_COLOR, fg="white") 
    recognizing_label.pack(side=LEFT, padx=10) 


    results_frame = tk.Frame(main_frame, bg=RESULT_BG, highlightbackground=BUTTON_COLOR,
                             highlightcolor=BUTTON_COLOR, highlightthickness=1)
    results_frame.pack(fill=BOTH, expand=True, pady=(0, 15))

    results_label = tk.Label(
        results_frame,
        text="Assistant Output:",
        font=INSTRUCTION_FONT,
        bg=RESULT_BG,
        fg=RESULT_FG,
        anchor="w"
    )
    results_label.pack(anchor="nw", padx=10, pady=(8, 0))

    result_scrollbar = Scrollbar(results_frame, orient=VERTICAL)
    result_scrollbar.pack(side="right", fill="y")

    result_display = Text(
        results_frame,
        height=7,
        relief="flat",
        state=DISABLED, 
        bg=RESULT_BG,
        fg=RESULT_FG,
        wrap=tk.WORD,
        yscrollcommand=result_scrollbar.set 
    )
    result_display.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

    result_scrollbar.config(command=result_display.yview)


    init_engine()

    root.mainloop()

if __name__ == "__main__":
    main()