import pyautogui
import time
import webbrowser

def book_movie_ticket_rpa():
    """Automates movie ticket booking using PyAutoGUI."""
    try:
        movie_name = input("🎬 Enter movie name: ").strip()
        city = input("📍 Enter city name: ").strip().lower()
        country = input("🌍 Enter country (India only): ").strip().lower()

        if country != "india":
            print("❌ Currently, this service is only available in India.")
            return "Sorry, ticket booking is only available for Indian cities."

        # Open BookMyShow for the selected city
        url = f"https://in.bookmyshow.com/explore/movies-{city.replace(' ', '-')}"
        webbrowser.open(url)
        time.sleep(5)  # Wait for page to load

        # Click on the search bar (Manually adjust coordinates)
        pyautogui.click(x=434, y=150)
        time.sleep(1)

        # Type movie name and press enter
        pyautogui.typewrite(movie_name, interval=0.1)
        pyautogui.press("enter")
        time.sleep(5)

        # Click first movie result (Manually adjust coordinates)
        pyautogui.click(x=628, y=246)
        time.sleep(5)

        # Click "Book Tickets"
        pyautogui.click(x=676, y=712)
        time.sleep(5)

        print(f"✅ Go through date and seats. Please confirm the payment manually.")
        return "Go through date and seats. Please confirm the payment manually."

    except Exception as e:
        print(f"❌ Error booking ticket: {e}")
        return "Error booking ticket. Please try again."
