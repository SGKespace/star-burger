from django.http import JsonResponse
from django.templatetags.static import static
import json
from .models import (
    Order,
    OrderItem,
    Product,
)
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from phonenumbers import parse as phone_parse, is_possible_number


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    try:
        data = request.data
    except ValueError:
        error = {'error': 'bad request'}
        return Response(
            error,
            status=status.HTTP_200_OK,
        )

    required_fiekds = [
        ['products', list],
        ['firstname', str],
        ['lastname', str],
        ['phonenumber', str],
        ['address', str],
    ]
    for required_field in required_fiekds:
        if required_field[0] not in data:
            return Response(
                {'error': f'{required_field[0]}: Required field'},
                status=status.HTTP_200_OK,
            )
        elif not data[required_field[0]]:
            return Response(
                {'error': f'{required_field[0]}: This field cannot be empty'},
                status=status.HTTP_200_OK,
            )
        elif not isinstance(data[required_field[0]], required_field[1]):
            return Response(
                {'error': f'{required_field[0]}: Expected {required_field[1]}'},
                status=status.HTTP_200_OK,
            )
        elif required_field[1] == list and len(data[required_field[0]]) == 0:
            return Response(
                {'error': f'{required_field[0]}: This list cannot be empty'},
                status=status.HTTP_200_OK,
            )
    if not is_possible_number(phone_parse(data['phonenumber'])):
        return Response(
            {'error': 'phonenumber: Invalid phone number entered'},
            status=status.HTTP_200_OK,
        )

    print(data)

    try:
        order = Order.objects.create(
            adress=data['address'],
            first_name=data['firstname'],
            second_name=data['lastname'],
            phone=data['phonenumber'],
        )

        for item in data['products']:
            product = Product.objects.get(
                id=item['product']
            )
            OrderItem.objects.create(
                item=product,
                count=item['quantity'],
                order=order,
            )
    except Product.DoesNotExist:
        return Response(
            {'error': f'products: Invalid primary key {item["product"]}'},
            status=status.HTTP_200_OK,
        )
    except Exception as exception:
        print(exception)
        return JsonResponse({
            'error': 'bad request',
        })

    return JsonResponse({})
