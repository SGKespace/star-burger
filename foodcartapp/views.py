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
from .serializers import OrderDeserializer, OrderSerializer


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
    data = request.data

    deserializer = OrderDeserializer(data=data)
    deserializer.is_valid(raise_exception=True)

    print(data)

    try:
        order = Order.objects.create(
            address=data['address'],
            firstname=data['firstname'],
            lastname=data['lastname'],
            phonenumber=data['phonenumber'],
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

        order_to_serialize = order.__dict__
        order_to_serialize['phonenumber'] = data['phonenumber']

        serializer = OrderSerializer(data=order_to_serialize)
        if serializer.is_valid():
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Product.DoesNotExist:
        return Response(
            {'error': f'products: Invalid primary key {item["product"]}'},
            status=status.HTTP_200_OK,
        )
    except Exception as exception:
        print(exception)
        return Response(
            {'error': 'bad request'},
            status=status.HTTP_200_OK,
        )

    # TODO это лишь заглушка
    return JsonResponse({})
