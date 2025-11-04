import graphene
from django.db import transaction
from graphql import GraphQLError
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from .models import Customer, Product, Order
from .serializer import OrderSerializers, ProductSerializer, CustomerSerializer
from .filters import ProductFilter, CustomerFilter, OrderFilter, FilteredConnectionField
import json


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (relay.Node, )


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (relay.Node, )


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
        filterset_class = OrderFilter
        interfaces = (relay.Node, )


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


class CustomerFilterInput(graphene.InputObjectType):
    """
    GraphQL filter input for the Customer model.
    Supports case-insensitive text search and date-based filtering.
    """
    name_icontains = graphene.String(
        description="Filter customers whose name contains this value (case-insensitive)"
    )
    email_icontains = graphene.String(
        description="Filter customers whose email contains this value (case-insensitive)"
    )
    phone_icontains = graphene.String(
        description="Filter customers whose phone number contains this value"
    )
    created_at_gte = graphene.Date(
        description="Filter customers created on or after this date"
    )
    created_at_lte = graphene.Date(
        description="Filter customers created on or before this date"
    )


class ProductFilterInput(graphene.InputObjectType):
    """
    GraphQL filter input for the Product model.
    Supports text search and numeric comparisons for price and stock.
    """
    name_icontains = graphene.String(
        description="Filter products whose name contains this value (case-insensitive)"
    )
    price_gte = graphene.Decimal(
        description="Filter products with price greater than or equal to this value"
    )
    price_lte = graphene.Decimal(
        description="Filter products with price less than or equal to this value"
    )
    stock_gte = graphene.Int(
        description="Filter products with stock greater than or equal to this value"
    )
    stock_lte = graphene.Int(
        description="Filter products with stock less than or equal to this value"
    )


class OrderFilterInput(graphene.InputObjectType):
    """
    GraphQL filter input for the Order model.
    Includes date filters and nested filters for related models.
    """
    order_date_gte = graphene.Date(
        description="Filter orders placed on or after this date"
    )
    order_date_lte = graphene.Date(
        description="Filter orders placed on or before this date"
    )

    # Nested filters
    customer = graphene.Argument(
        CustomerFilterInput,
        description="Nested filter for related customer fields"
    )
    product = graphene.Argument(
        ProductFilterInput,
        description="Nested filter for related product fields"
    )



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


class OrderByEnum(graphene.Enum):
    NAME_ASC = "name"
    NAME_DESC = "-name"
    PRICE_ASC = "price"
    PRICE_DESC = "-price"
    ORDER_DATE_ASC = "order_date"
    ORDER_DATE_DESC = "-order_date"


class Query(graphene.ObjectType):
    all_customers = FilteredConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = FilteredConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = FilteredConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(order_by.value)
        return qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(order_by.value)
        return qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(order_by.value)
        return qs



class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
