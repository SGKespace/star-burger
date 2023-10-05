import requests
import os

from django import forms, setup
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from environs import Env
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from sql_util.utils import SubquerySum
from geopy import distance


from foodcartapp.models import Product, Restaurant, Order, OrderItem
from geo_data.models import GeoData
from django.db.models import F


os.environ['DJANGO_SETTINGS_MODULE'] = 'star_burger.settings'
setup()

env = Env()
env.read_env()


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(apikey, address):
    try:
        geo_data = GeoData.objects.get(address=address)
        print(geo_data.created_at)
        lon = geo_data.longitude
        lat = geo_data.latitude
    except GeoData.DoesNotExist:
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(
            base_url, params={
                'geocode': address,
                'apikey': apikey,
                'format': "json",
            },
            timeout=1,
        )
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        GeoData.objects.create(
            address=address,
            latitude=lat,
            longitude=lon,
        )
    return lon, lat


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    yandex_api_key = env('YANDEX_API_KEY')

    orders = Order.objects.all()\
        .prefetch_related('products__item__menu_items__restaurant')
    for order in orders:
        order_coordinates = fetch_coordinates(yandex_api_key, order.address)
        order_restaurants = set()
        order_items = order.products.all()
        for order_item in order_items:
            for menu_item in order_item.item.menu_items.all():
                if (menu_item.restaurant, ) not in order_restaurants:
                    restaurant_coordinates = fetch_coordinates(
                        yandex_api_key, menu_item.restaurant.address
                    )
                    distance_restaurant_order = distance.distance(
                        restaurant_coordinates[::-1],
                        order_coordinates[::-1],
                    ) if order_coordinates and restaurant_coordinates else None

                    order_restaurants.add((
                        menu_item.restaurant,
                        distance_restaurant_order,
                    ))
        order_restaurants = list(order_restaurants)
        order_restaurants = sorted(
            order_restaurants,
            key=lambda restaurant: restaurant[1] if restaurant[1] else 0
        )
        order.restaurants = order_restaurants


    orders.annotate(
        cost=SubquerySum(F('products__previous_price')*F('products__count')),
    )

    return render(request, template_name='order_items.html', context={
        'order_items': orders,
    })
