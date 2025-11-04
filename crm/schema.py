import graphene
from django.db import transaction
from graphql import GraphQLError
from graphene_django.types import DjangoObjectType
from .models import Customer, Product, Order
from .serializer import OrderSerializers, ProductSerializer, CustomerSerializer
import json


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer


class ProductType(DjangoObjectType):
    class Meta:
        model = Product


class OrderType(DjangoObjectType):
    total_amount = graphene.Decimal()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "products",
            "order_date",
            "total_amount",
        ]


class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)
    order_date = graphene.Date()


class CreateCustomer(graphene.Mutation):
    """
    Create Customer Mutation
    """
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        serializer = CustomerSerializer(data=input)
        if not serializer.is_valid():
            raise GraphQLError(json.dumps(serializer.errors))

        customer = serializer.save()
        return CreateCustomer(
            customer=customer, message='Customer created successfully!')


class BulkCreateCustomers(graphene.Mutation):
    """
    Bulk Create Customer Mutation
    """
    class Arguments:
        input = graphene.List(CustomerInput)

    customers = graphene.List(CustomerType)
    errors = graphene.String()

    def mutate(self, info, input):
        valid_customers = []
        errors = []

        for i, data in enumerate(input):
            serializer = CustomerSerializer(data=data)
            if not serializer.is_valid():
                errors.append(serializer.errors)
                continue

            valid_customers.append(Customer(**serializer.validated_data))

        created_customers = []
        if valid_customers:
            with transaction.atomic():
                created_customers = Customer.objects.bulk_create(
                    valid_customers)

        return BulkCreateCustomers(
            customers=created_customers, errors=json.dumps(errors))


class CreateProduct(graphene.Mutation):
    """
    Create Product Mutation
    """
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()

    def mutate(self, info, input):
        serializer = ProductSerializer(data=input)
        if not serializer.is_valid():
            raise GraphQLError(json.dumps(serializer.errors))

        product = serializer.save()
        return CreateProduct(
            product=product, message='Product created successfully!')


class CreateOrder(graphene.Mutation):
    """
    Create Order Mutation
    """
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()

    def mutate(self, info, input):
        serializer = OrderSerializers(data={
            "customer": input.customer_id,
            "products": input.product_ids,
            "order_date": input.order_date,
        })
        if not serializer.is_valid():
            raise GraphQLError(json.dumps(serializer.errors))

        order = serializer.save()
        return CreateOrder(order=order)


class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_all_orders(self, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
