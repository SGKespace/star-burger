from rest_framework import serializers, status
from rest_framework.exceptions import APIException
from .models import Order, Product, OrderItem


class OrderItemDeserializer(serializers.ModelSerializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField()
    order_id = serializers.IntegerField()

    def create(self, validated_data):
        product = Product.objects.get(id=validated_data['product'])
        order = Order.objects.get(id=validated_data['order_id'])
        return OrderItem.objects.create(
            item=product,
            previous_price=product.price,
            count=validated_data['quantity'],
            order=order,
        )

    class Meta:
        model = OrderItem
        fields = [
            'product',
            'quantity',
            'order_id',
        ]


class ProductsValidationException(APIException):
    status_code = status.HTTP_200_OK
    default_detail = 'Invalid primary key'


class OrderDeserializer(serializers.ModelSerializer):
    products = serializers.ListField(allow_empty=False)

    def create(self, validated_data):
        try:
            if 'products' in validated_data:
                for item in validated_data['products']:
                    Product.objects.get(
                        id=item['product']
                    )
                del validated_data['products']
        except Product.DoesNotExist as exception:
            raise ProductsValidationException(
                detail={
                    'error': f'products: Invalid primary key {item["product"]}'
                },
            ) from exception
        return Order.objects.create(**validated_data)

    class Meta:
        model = Order
        fields = [
            'address',
            'firstname',
            'lastname',
            'phonenumber',
            'products',
        ]


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            'id',
            'firstname',
            'lastname',
            'address',
        ]
