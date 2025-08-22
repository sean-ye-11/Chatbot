import requests
import os
from dotenv import load_dotenv

# Latter tell them the .env and the way to access api key
load_dotenv()
api_key = os.getenv("WEATHER_API_KEY")

def get_temperature(latitude, longitude):
    response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={latitude},{longitude}&aqi=no")
    data = response.json()
    return data['current']['temp_c']

if __name__ == "__main__":
    print("Toronto:")
    print(get_temperature(43.6532, -79.3832))
    print("Hong Kong:")
    print(get_temperature(22.3193, 114.1694))
    print("Paris:")
    print(get_temperature(48.8575, 2.3514))