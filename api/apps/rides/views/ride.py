from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status as drf_status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Prefetch
from django.utils import timezone

from ..models import Ride, RideEvent
from ..serializers import (
    RideListSerializer,
    RideDetailSerializer,
    RideListQueryParamSerializer,
    RideStatusUpdateSerializer,
)
from ..filters import RideOrdering, RideFiltering
from ..utils import validate_query_params
from ..services import format_event_description
from apps.users.permissions import AdministratorPermission

class StandardRidePagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'p'
    page_size_query_param = 'ps'
    max_page_size = 20
    
class RideViewSet(ModelViewSet):
    permission_classes = [AdministratorPermission]
    ordering = ['id']
    pagination_class = StandardRidePagination
    filter_backends = [RideOrdering, RideFiltering]
    serializer_class = RideListSerializer
    
    def perform_create(self, serializer):
        ride = serializer.save()
        RideEvent.objects.create(
            ride=ride,
            description=format_event_description(ride.status, ride),
            occurred_at=timezone.now(),
        )

    def get_serializer_class(self):
        if self.action in ('retrieve', 'status'):
            return RideDetailSerializer
        return RideListSerializer

    def get_queryset(self):
        if self.action == 'list':
            time_threshold = timezone.now() - timezone.timedelta(hours=24)
            return Ride.objects.prefetch_related(
                Prefetch(
                    'events',
                    queryset=RideEvent.objects.filter(created_at__gte=time_threshold),
                    to_attr='todays_ride_events',
                )
            )
        return Ride.objects.prefetch_related(
            Prefetch(
                'events',
                queryset=RideEvent.objects.all().order_by('occurred_at', 'created_at', 'id'),
            )
        )
    
    @validate_query_params(serializer = RideListQueryParamSerializer)
    def list(self, request):
        return super().list(request)

    @action(detail=True, methods=['post'], url_path='status')
    def status(self, request, pk=None):
        ride = self.get_object()
        serializer = RideStatusUpdateSerializer(
            instance=ride,
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        updated_ride = self.get_queryset().get(pk=ride.pk)
        return Response(
            RideDetailSerializer(
                updated_ride,
                context=self.get_serializer_context(),
            ).data,
            status=drf_status.HTTP_200_OK,
        )


class NaiveRideViewSet(ModelViewSet):
    permission_classes = [AdministratorPermission]
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
