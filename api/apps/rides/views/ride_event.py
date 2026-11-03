from rest_framework import status as drf_status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..models import RideEvent
from ..serializers import BaseRideEventSerializer, RideEventCorrectionInputSerializer
from apps.users.permissions import AdministratorPermission


class RideEventViewSet(ReadOnlyModelViewSet):
    permission_classes = [AdministratorPermission]
    queryset = RideEvent.objects.all()
    serializer_class = BaseRideEventSerializer

    @action(detail=True, methods=['post'], url_path='correct')
    def correct(self, request, pk=None):
        event = self.get_object()
        serializer = RideEventCorrectionInputSerializer(
            data=request.data,
            context={'event': event, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        updated_event = serializer.save()
        return Response(
            BaseRideEventSerializer(updated_event).data,
            status=drf_status.HTTP_200_OK,
        )
