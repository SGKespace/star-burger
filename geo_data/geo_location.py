import os
import requests
from django import setup
from django.conf import settings
from django.db import models
from django.utils.timezone import now


os.environ['DJANGO_SETTINGS_MODULE'] = 'star_burger.settings'


def get_or_create_locations(address, apikey=settings.YANDEX_API_KEY):
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(
            base_url,
            params={
                'geocode': address,
                'apikey': apikey,
                'format': "json",
            },
            timeout=10,
        )
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        return GeoData.objects.create(
            address=address,
            latitude=lat,
            longitude=lon,
        )
