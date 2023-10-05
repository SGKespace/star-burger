from django.http import JsonResponse
from django.db import transaction
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .models import Product
from .serializers import OrderDeserializer, OrderSerializer, OrderItemDeserializer


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


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    data = request.data

    deserializer = OrderDeserializer(data=data)
    deserializer.is_valid(raise_exception=True)
    order = deserializer.save()

    try:
        for item in data['products']:
            item['order_id'] = order.id
            order_item_deserializer = OrderItemDeserializer(data=item)
            order_item_deserializer.is_valid(raise_exception=True)
            order_item_deserializer.save()

        serializer = OrderSerializer(data=order.__dict__)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception:
        order.delete()
        return Response(
            {'error': 'bad request'},
            status=status.HTTP_200_OK,
        )
