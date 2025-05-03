import requests
import wikipedia
import pywhatkit as kit
import webbrowser

from email.message import EmailMessage
from decouple import config
import pyjokes

def tell_joke():
    """Fetch a random joke and return it."""
    joke = pyjokes.get_joke()
    print(joke)
    return joke

def find_my_ip():
    ip_address = requests.get('https://api.ipify.org?format=json').json()
    return ip_address['ip']

def search_on_wikipedia(queri):
    results = wikipedia.summary(queri, sentences=2 )
    return results

def search_on_google(queri):
    webbrowser.open(f"https://www.google.com/search?q={queri}")

def youtube(video):
    webbrowser.open(f"https://www.youtube.com/results?search_query={video}")


def get_news():
    news_headlines = []
    results = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=7ae369443afe498987c86c59c9b5b77e").json()
    articles = results['articles']
    for article in articles:
        news_headlines.append(article['title'])
    return news_headlines[:5]

def weather_forecate(city):
    res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=dba271293557ca6238fbf58ed9082755").json()

    weather = res["weather"][0]["main"]
    temp = round(res["main"]["temp"] - 273.15)  
    feels_like = round(res["main"]["feels_like"] - 273.15)  
    humidity = res["main"]["humidity"]

    return weather,f" {temp} °C",f" {feels_like}°C",f" {humidity}%"

API_KEY = "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"