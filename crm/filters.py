import django_filters
from graphene_django.filter import DjangoFilterConnectionField
import graphene
from crm.models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    phone_pattern = django_filters.CharFilter(field_name='phone', method='match_phone')
    class Meta:
        model = Customer
        fields = {
            'name': ['iexact'],
            'email': ['icontains'],
            'created_at': ['gte', 'lte'],
        }
    
    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'created_at'),
        )
    )

    def match_phone(self, queryset, name, value):
        return queryset.filter(phone_number__icontains=value)


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'price': ['lte', 'gte'],
            'stock': ['exact', 'gte', 'lte', ],
        }

    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'price'),
        )
    )

class OrderFilter(django_filters.FilterSet):
    total_amount__gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount__lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    product__name = django_filters.CharFilter(field_name='product_name', lookup_expr='icontains')
    customer_name = django_filters.CharFilter(field_name='customer_name', lookup_expr='icontains')
    class Meta:
        model = Order
        fields = {
            'order_date': ['gte', 'lte'],
        }
    order_by = django_filters.OrderingFilter(
        fields=(
            ('order_date'),
        )
    )


class FilteredConnectionField(DjangoFilterConnectionField):
    """Custom field that adds a `filter` input argument."""
    @classmethod
    def resolve_queryset(cls, connection, iterable, info, args):
        filterset_class = cls.filterset_class
        if 'filter' in args and filterset_class:
            filter_data = args.get('filter', {})
            qs = filterset_class(data=filter_data, queryset=iterable).qs
        else:
            qs = iterable
        return qs

    @classmethod
    def field_args(cls, registry, model, node_type):
        # Instead of exposing each filter arg individually,
        # we nest them under a single `filter` argument
        filterset_class = cls.filterset_class
        filter_input_type = graphene.InputObjectType(
            f"{model.__name__}FilterInput",
            **{
                name: graphene.String()  # You can refine types here
                for name in filterset_class.get_filters()
            }
        )
        args = super().field_args(registry, model, node_type)
        args.pop('filters', None)
        args['filter'] = graphene.Argument(filter_input_type)
        return args
