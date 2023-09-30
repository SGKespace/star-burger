from rest_framework import serializers
from .models import Order
from phonenumber_field.modelfields import PhoneNumberField


class OrderDeserializer(serializers.ModelSerializer):
    products = serializers.ListField(allow_empty=False)

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
            'phonenumber',
            'address',
        ]
