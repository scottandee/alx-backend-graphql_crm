from django.db import models
from django.core.validators import MinValueValidator


class Customer(models.Model):
    name = models.CharField(max_length=75)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12, null=True)


class Product(models.Model):
    name = models.CharField(max_length=75)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0, null=True)


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='orders')
    order_date = models.DateField(auto_now_add=True)

    @property
    def total_amount(self):
        total_amount = 0
        for p in self.products.all():
            total_amount += p.price
        return total_amount
