import django_filters
from django.db.models import Sum
from crm.models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    """
    Customer Filter
    """
    phone_pattern = django_filters.CharFilter(
        field_name='phone', method='match_phone')
    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('created_at', 'created_at')
        )
    )

    class Meta:
        model = Customer
        fields = {
            'name': ['icontains'],
            'email': ['icontains'],
            'created_at': ['gte', 'lte'],
        }

    def match_phone(self, queryset, name, value):
        """
        Match phone numbers that begin with a certain pattern
        """
        return queryset.filter(phone__startswith=value)


class ProductFilter(django_filters.FilterSet):
    """
    Product Filter
    """
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('stock', 'stock'),
            ('price', 'price'),
        )
    )

    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'price': ['lte', 'gte'],
            'stock': ['exact', 'gte', 'lte', ],
        }

    def filter_low_stock(self, queryset, name, value):
        """
        This method returns products with low stock if
        value is set to true
        """
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


class OrderFilter(django_filters.FilterSet):
    """
    Order Filter
    """
    total_amount__gte = django_filters.NumberFilter(
        method='filter_total_amount_gte')
    total_amount__lte = django_filters.NumberFilter(
        method='filter_total_amount_lte')
    product_name = django_filters.CharFilter(
        field_name='products__name', lookup_expr='icontains')
    customer_name = django_filters.CharFilter(
        field_name='customer__name', lookup_expr='icontains')
    order_by = django_filters.OrderingFilter(
        fields=(('order_date', 'order_date')))

    class Meta:
        model = Order
        fields = {
            'order_date': ['gte', 'lte'],
        }

    def filter_total_amount_gte(self, queryset, name, value):
        """
        This method returns orders with total amount greater
        than value
        """
        return queryset.annotate(
            total=Sum('products__price')).filter(total__gte=value)

    def filter_total_amount_lte(self, queryset, name, value):
        """
        This method returns orders with total amount less
        than value
        """
        return queryset.annotate(
            total=Sum('products__price')).filter(total__lte=value)
