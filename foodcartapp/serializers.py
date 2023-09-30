from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.ListField(allow_empty=False)

    class Meta:
        model = Order
        fields = ['address', 'firstname', 'lastname', 'phonenumber', 'products']
