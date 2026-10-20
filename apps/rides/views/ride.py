from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework.decorators import action
from http import HTTPMethod
from rest_framework.permissions import IsAdminUser

from ..models import Ride, RideEvent
from ..serializers import RideListSerializer, RideListQueryParamSerializer
from ..filters import RideOrdering, RideFiltering
from ..utils import validate_query_params

class StandardRidePagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'p'
    page_size_query_param = 'ps'
    max_page_size = 20
    
class RideViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    pagination_class = StandardRidePagination
    filter_backends = [RideOrdering, RideFiltering]
    serializer_class = RideListSerializer

    def get_queryset(self):
        time_threshold = timezone.now() - timezone.timedelta(hours=24)
        
        return Ride.objects.prefetch_related(
            Prefetch(
                'events',
                queryset = RideEvent.objects.filter(
                    created_at__gte = time_threshold
                    ),
                to_attr = 'todays_ride_events'
            )
        )
    
    @validate_query_params(serializer = RideListQueryParamSerializer)
    def list(self, request):
        return super().list(request)

class NaiveRideViewSet(ModelViewSet):
    pagination_class = StandardRidePagination
    filter_backends = [RideOrdering, RideFiltering]
    serializer_class = RideListSerializer
    queryset = Ride.objects.all()
    
    @validate_query_params(serializer = RideListQueryParamSerializer)
    def list(self, request):
        queryset = super().filter_queryset(self.queryset)
        page = self.paginate_queryset(queryset)
        time_threshold = timezone.now() - timezone.timedelta(hours=24)

        for ride in page or queryset:
            ride.todays_ride_events = list(ride.events.filter(created_at__gte=time_threshold))
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
       
        serialized = self.get_serializer(queryset, many = True)
        return Response(serialized.data)
