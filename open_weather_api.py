import requests

from keys import API_KEY


def get_city(city_name):
    """
    Returns coordinates of the city if exists. None if doesn't
    :param city_name: Name of the city
    :return: coordinates / None
    """
    r = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=5&appid={API_KEY}')
    try:
        if r.json()[0]:
            return r.json()[0]['lat'], r.json()[0]['lon']
    except IndexError:
        return None


def get_weather(city_name):
    """
    Returns temperature, weather state, name and time zone based on coordinates
    :param city_name: geo coordinates
    :return: dict with weather information
    """
    city = get_city(city_name)
    if city:
        lat, lon = city
        r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}')
        return {
            'temp': r.json()['main']['temp'],
            'state': r.json()['weather'][0]['description'],
            'city_name': city_name,
            'timezone': r.json()['timezone']
                }
    return None
