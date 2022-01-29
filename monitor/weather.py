from json.decoder import JSONDecodeError
from pydantic import BaseModel
import requests
import logging
from model import GenerateReportRequest, Metadata, Weather

from requests.models import HTTPError

API_KEY = "6ba5c171f25f47b9055756f64ba1a3c9"

class Error(Exception):
    """Base exception class"""
    pass

class WeatherError(Error):
    """Raised when weather data cannot be fetched"""
    def __init__(self):
        self.message = 'Could not get weather data.'
    
def get_weather_info(location: str) -> Weather:
    try:
        response = requests.get(
            "http://api.openweathermap.org/data/2.5/weather?q=" + location + "&units=metric&APPID=" + API_KEY)
        
        weather_json = response.json()
        print(weather_json)
        weather = Weather(location=location, 
                        temperature=str(weather_json['main']['temp']), 
                        description=weather_json['weather'][0]['description'], 
                        pressure=weather_json['main']['pressure'],
                        humidity=weather_json['main']['humidity'])
    except (HTTPError, KeyError, JSONDecodeError, ValueError) as error:
        logging.error(error)
        raise WeatherError
    
    return weather

def process_weather(metadata: Metadata, request: GenerateReportRequest):
    logging.info("Checking weather...")
    try:
        metadata.weather = get_weather_info(location=request.location)
        logging.info('[OK] Weather data fetched.')
    except WeatherError as e:
        logging.error(e)