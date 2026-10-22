from django.db.models import F, FloatField, Value
from django.db.models.functions import ASin, Cos, Radians, Sin, Sqrt, Power
from django.template import loader
from rest_framework.filters import OrderingFilter, BaseFilterBackend

from ..models import Statuses


class RideFiltering(BaseFilterBackend):
    filter_fields = {
        'rider_email': 'id_rider__email',
        'status': 'status',
    }
    template = 'ride_filter_form.html'

    def filter_queryset(self, request, queryset, view):
        filters = {}
        validated_params = getattr(request, 'validated_query_params', {})
        for param, lookup in self.filter_fields.items():
            value = validated_params.get(param)
            if value not in (None, ''):
                filters[lookup] = value
        return queryset.filter(**filters) if filters else queryset

    def to_html(self, request, queryset, view):
        template = loader.get_template(self.template)
        return template.render({
                'request': request,
                'params': request.query_params,
                'status_choices': Statuses.choices
                })

class RideOrdering(OrderingFilter):
    ordering_param = 'sort_by'
    ordering_fields = ['pickup_time', 'distance']

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if ordering and any(field.lstrip('-') == 'distance' for field in ordering):
            queryset = queryset.annotate(distance=self.get_distance_query(request))

        return queryset.order_by(*ordering) if ordering else queryset

    def get_distance_query(self, request):
        validated_params = request.validated_query_params
        target_lat = float(validated_params['target_lat'])
        target_long = float(validated_params['target_long'])
        earth_radius_km = 6371.0

        target_lat_rad = Radians(Value(target_lat, output_field=FloatField()))
        target_long_rad = Radians(Value(target_long, output_field=FloatField()))

        pickup_lat_rad = Radians(F('pickup_latitude'))
        pickup_lon_rad = Radians(F('pickup_longitude'))

        deltax = pickup_lat_rad - target_lat_rad
        delaty = pickup_lon_rad - target_long_rad

        haversine_a = (
            Power(Sin(deltax / 2), 2) + 
            Cos(target_lat_rad) * Cos(pickup_lat_rad) * Power(Sin(delaty / 2), 2)
        )

        return 2 * earth_radius_km * ASin(Sqrt(haversine_a))