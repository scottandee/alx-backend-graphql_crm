from rest_framework import serializers
from .models import Customer, Product, Order
import re


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone']
        read_only_fields = ['id']

    def validate_phone(self, value):
        """
        Validate phone format (e.g., +1234567890 or 123-456-7890)
        """
        pattern = re.compile(r"^(\+\d{1,15}|(\d{3}-\d{3}-\d{4}))$")
        if not pattern.match(str(value)):
            raise serializers.ValidationError(
                "Invalid phone number format. Use +1234567890 or 123-456-7890."
            )
        return value


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']
        read_only_fields = ['id']


class OrderSerializers(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all())
    products = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), many=True)

    class Meta:
        model = Order
        fields = ['customer', 'products', 'total_amount', 'order_date']
        read_only_fields = ['id']
