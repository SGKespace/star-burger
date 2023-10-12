from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem


class OrderItemDeserializer(serializers.ModelSerializer):

    @transaction.atomic
    def create(self, validated_data):
        product = validated_data['product']
        return OrderItem.objects.create(
            product=product,
            previous_price=product.price,
            quantity=validated_data['quantity'],
            order=Order.objects.get(id=self.__dict__['initial_data']['order']),
        )

    class Meta:
        model = OrderItem
        fields = (
            'product',
            'quantity',
        )


class OrderDeserializer(serializers.ModelSerializer):
    products = OrderItemDeserializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product in products:
            product['order'] = order.id
            product['product'] = product['product'].id
            order_item_deserializer = OrderItemDeserializer(data=product)
            order_item_deserializer.is_valid(raise_exception=True)
            order_item_deserializer.save()
        return order

    class Meta:
        model = Order
        fields = (
            'products',
            'address',
            'firstname',
            'lastname',
            'phonenumber',
        )
        depth = 1
